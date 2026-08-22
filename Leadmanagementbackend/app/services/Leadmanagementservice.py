from math import ceil

from app.DTOs.Leadlist import LeadlistDTO, Leadetails
from app.enums.channel import ConnectionStatus
from app.models import Lead


class LeadService:

    def __init__(
        self,
        lead_repository,
        channel_connection_repository,
    ):
        self.lead_repository = lead_repository
        self.channel_connection_repository = (
            channel_connection_repository
        )

    async def create_or_update_lead(
            self,
            channel_id: int,
            identifier: str,
            name: str | None = None,
            email: str | None = None,
            phone_number: str | None = None,

    ):

        connection = (
            self.channel_connection_repository
            .get_by_provider_identifier(
                provider_account_identifier=identifier,
                channel_id=channel_id,

            )
        )

        if connection is None:
            raise ValueError(
                "No connected channel found for identifier."
            )

        lead = (
            self.lead_repository
            .get_by_identifier(
                channel_connection_id=connection.id,
                tenant_id=1,
                identifier=identifier,
            )
        )

        if lead is not None:

            if name:
                lead.name = name

            if email:
                lead.email = email

            if phone_number:
                lead.phone_number = phone_number

            self.lead_repository.update(lead)
            return lead

        lead = Lead(
            tenant_id=connection.tenant_id,
            channel_connection_id=connection.id,
            name=name,
            email=email,
            phone_number=phone_number,
        )

        return self.lead_repository.save(
            lead
        )





    async def get_lead_by_channel_id(
                self,
                channel_id: int,
                page: int = 1,
                page_size: int = 20,
                sort_by: str = "created_at",
                sort_order: str = "desc",
        ) -> LeadlistDTO:
            offset = (
                             page - 1
                     ) * page_size

            all_leads, total = (
                self.lead_repository
                .get_leads_by_channel_id(
                    channel_id=channel_id,
                    limit=page_size,
                    offset=offset,
                    sort_by=sort_by,
                    sort_order=sort_order,
                )
            )

            valid_leads = []

            for lead_details in all_leads:
                valid_leads.append(
                    Leadetails(
                        id=lead_details.id,
                        name=lead_details.name,
                        email=lead_details.email,
                        phone_number=lead_details.phone_number,
                        created_at=lead_details.created_at,
                    )
                )

            return LeadlistDTO(
                channel_id=channel_id,
                Leaddetails=valid_leads,
                page=page,
                page_size=page_size,
                total=total,
                total_pages=ceil(
                    total / page_size
                ) if total > 0 else 0,
            )












