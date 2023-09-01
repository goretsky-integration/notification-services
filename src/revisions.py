import pathlib
from datetime import timedelta, datetime

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

from core import load_config_from_file, setup_logging
from message_queue_events import RevisionEvent
from services import message_queue
from services.converters import UnitsConverter
from services.external_dodo_api import DatabaseAPI, AuthAPI
from services.period import get_moscow_now


class RevisionSummaryUnit(BaseModel):
    percent_of_revenue: float
    amount: float


class RevisionSummary(BaseModel):
    total_loss: RevisionSummaryUnit
    unaccounted_losses: RevisionSummaryUnit
    write_offs: RevisionSummaryUnit
    total_excess: RevisionSummaryUnit


class NearestRevision(BaseModel):
    id: int
    at: datetime


def parse_nearest_revisions_html(
        html: str,
) -> list[NearestRevision]:
    soup = BeautifulSoup(html, 'lxml')
    options = soup.find_all('option')

    nearest_revisions: list[NearestRevision] = []
    for option in options:
        revision_id: str = option['value']
        date, time, period = option.text.strip().split()
        if not 'день' in period.lower():
            continue
        revision_at = datetime.strptime(f'{date} {time}', '%d.%m.%Y %H:%M')
        nearest_revisions.append(
            NearestRevision(
                id=revision_id,
                at=revision_at,
            ),
        )

    return nearest_revisions


def parse_revisions_html_page(html: str) -> RevisionSummary:
    soup = BeautifulSoup(html, 'lxml')
    tbody = soup.find('tbody')
    trs = tbody.find_all('tr')
    _, percent_of_value1, amount1 = [td.text.replace(',', '.').replace(' ', '')
                                     for td in trs[0].find_all('td')]
    _, percent_of_value2, amount2 = [td.text.replace(',', '.').replace(' ', '')
                                     for td in trs[1].find_all('td')]
    _, percent_of_value3, amount3 = [td.text.replace(',', '.').replace(' ', '')
                                     for td in trs[2].find_all('td')]
    _, percent_of_value4, amount4 = [td.text.replace(',', '.').replace(' ', '')
                                     for td in trs[5].find_all('td')]

    return RevisionSummary(
        total_loss=RevisionSummaryUnit(percent_of_revenue=percent_of_value1,
                                       amount=amount1),
        unaccounted_losses=RevisionSummaryUnit(
            percent_of_revenue=percent_of_value2, amount=amount2),
        write_offs=RevisionSummaryUnit(percent_of_revenue=percent_of_value3,
                                       amount=amount3),
        total_excess=RevisionSummaryUnit(percent_of_revenue=percent_of_value4,
                                         amount=amount4),
    )


def get_latest_revision_for_date_or_none(
        date: datetime,
        revisions: list[NearestRevision],
) -> NearestRevision | None:
    revisions_for_date = [
        revision
        for revision in revisions
        if revision.at.date() == date.date()
    ]
    if not revisions_for_date:
        return None

    return max(revisions_for_date, key=lambda r: r.at)


def main() -> None:
    config_file_path = pathlib.Path(__file__).parent.parent / 'config.toml'
    config = load_config_from_file(config_file_path)

    now = get_moscow_now()
    yesterday = now - timedelta(days=1)

    setup_logging(loglevel=config.logging.level,
                  logfile_path=config.logging.file_path)

    with httpx.Client(
            base_url=config.api.database_api_base_url) as database_client:
        units = DatabaseAPI(database_client).get_units()
    units = UnitsConverter(units)

    events = []
    with httpx.Client(base_url=config.api.auth_api_base_url) as auth_client:
        auth_api = AuthAPI(auth_client)

        for unit in units.units:

            account_cookies = auth_api.get_account_cookies(
                account_name=unit.office_manager_account_name,
            )

            base_url = f'https://officemanager.dodopizza.{config.country_code}'
            try:
                with httpx.Client(base_url=base_url,
                                  cookies=account_cookies.cookies) as http_client:
                    params = {
                        'unitId': unit.id,
                        'date': f'{now:%d.%m.%Y}',
                    }
                    url = '/InventoryManager/LossesAndExcees/SelectNearestRevisions'
                    response = http_client.get(url, params=params)

                    response_data = response.json()
                    html: str = response_data['html']
                    nearest_revisions_today = parse_nearest_revisions_html(html)

                    params = {
                        'unitId': unit.id,
                        'date': f'{yesterday:%d.%m.%Y}',
                    }
                    response = http_client.get(url, params=params)

                    response_data = response.json()
                    html: str = response_data['html']
                    nearest_revisions_yesterday = parse_nearest_revisions_html(
                        html)

                    latest_revision_today = get_latest_revision_for_date_or_none(
                        date=now,
                        revisions=nearest_revisions_today,
                    )
                    latest_revision_yesterday = get_latest_revision_for_date_or_none(
                        date=yesterday,
                        revisions=nearest_revisions_yesterday,
                    )
                    if not all(
                            (latest_revision_yesterday, latest_revision_today)):
                        continue

                    data = {
                        'UnitId': unit.id,
                        'SelectedMaterialCategories': [1, 2, 3, 5],
                        'DefaultBeginDateString': f'{yesterday:%d.%m.%Y}',
                        'DefaultEndDateString': f'{now:%d.%m.%Y}',
                        'firstRevisionId': latest_revision_yesterday.id,
                        'secondRevisionId': latest_revision_today.id,
                        'IsVatIncluded': True,
                    }
                    url = '/InventoryManager/LossesAndExcees/LossesAndExceesData'

                    response = http_client.post(url, data=data)
                    revisions_summary = parse_revisions_html_page(response.text)
            except Exception:
                pass
            else:
                events.append(RevisionEvent(
                    unit_id=unit.id,
                    unit_name=unit.name,
                    revision=revisions_summary,
                ))
    with message_queue.get_message_queue_channel(
            config.message_queue.rabbitmq_url
    ) as message_queue_channel:
        message_queue.send_events(message_queue_channel, events)


if __name__ == '__main__':
    main()
