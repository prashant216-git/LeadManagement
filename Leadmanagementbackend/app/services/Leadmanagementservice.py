from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from app.DTOs.ChannelLeadidentifier import LeadChannelIdentifiersDTO, ChannelIdentifierDTO
from app.DTOs.CreateManualLeadDTO import CreateManualLeadDTO
from app.DTOs.Leadlist import LeadlistDTO, Leadetails
from app.enums.channel import ConnectionStatus
from app.models import Lead
from app.core.lock import (
    lead_lock_manager,
)


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
            source_channel_id: UUID,
            identifier: str,
            name: str | None = None,
            email: str | None = None,
            phone_number: str | None = None,

    ):

        print("entered leadservice")

        connection = (
            self.channel_connection_repository
            .get_by_provider_identifier(
                provider_account_identifier=identifier,
                channel_id=source_channel_id,

            )
        )

        if connection is None:
            raise ValueError(
                "No connected channel found for identifier."
            )



        lock_key = (
            f"lead:{source_channel_id}:"
            f"{identifier.lower()}"
        )

        lock = lead_lock_manager.get_lock(
            lock_key
        )

        with lock:
            lead = (
                self.lead_repository
                .get_by_identifier(
                    user_id=connection.user_id,
                    source_channel_id=source_channel_id,

                    email=email,
                    phone_number=phone_number,
                )
            )

            if lead is not None:
                print("got old")

                if name:
                    lead.name = name

                if email:
                    lead.email = email

                if phone_number:
                    lead.phone_number = phone_number

                self.lead_repository.update(lead)
                return lead

            print("creating new")

            lead = Lead(
                user_id=connection.user_id,
                source_channel_id=source_channel_id,
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
            channel_id: UUID,
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
                user_id = UUID("9ad69636-f013-49f6-9cce-00f2828dbc6f"),
                channel_id=channel_id,
                limit=page_size,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        )

        valid_leads = []

        for (
                lead_details,
                source_identifier,
        ) in all_leads:
            valid_leads.append(
                Leadetails(
                    connection_id=(
                        lead_details.channel_connection_id
                    ),

                    source_identifier=(
                        source_identifier
                    ),

                    id=lead_details.id,

                    name=lead_details.name,

                    email=lead_details.email,

                    phone_number=lead_details.phone_number,

                    created_at=(
                        lead_details.created_at
                    ),
                )
            )

        return LeadlistDTO(
            channel_id=channel_id,

            Leaddetails=valid_leads,

            page=page,

            page_size=page_size,

            total=total,

            total_pages=(
                ceil(total / page_size)
                if total > 0
                else 0
            ),
        )

    async def create_manual_lead(
            self,
            user_id: UUID,
            lead_data: CreateManualLeadDTO,
    ) -> Lead:

        lead = None

        # Find existing lead by email
        lead =await self.lead_repository.get_by_identifier(user_id=user_id,


                    email=lead_data.email,
                    phone_number=lead_data.email,)

        # --------------------------------------------------
        # Existing lead
        # --------------------------------------------------

        if lead is not None:

            if lead_data.name:
                lead.name = lead_data.name

            if lead_data.email:
                lead.email = lead_data.email

            if lead_data.phone_number:
                lead.phone_number = lead_data.phone_number

            lead.updated_at = datetime.now(timezone.utc)

            await self.lead_repository.save(lead)

            return lead


        lead = Lead(
            user_id=user_id,
            source_channel_id=None,
            name=lead_data.name,
            email=lead_data.email,
            phone_number=lead_data.phone_number,
        )

        return self.lead_repository.save(
            lead
        )

    async def get_manual_leads(
            self,
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
            .get_manual_leads(
                user_id = UUID("9ad69636-f013-49f6-9cce-00f2828dbc6f"),
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
                    connection_id=(
                        lead_details.channel_connection_id
                    ),

                    source_identifier=None,

                    id=lead_details.id,

                    name=lead_details.name,

                    email=lead_details.email,

                    phone_number=lead_details.phone_number,

                    created_at=lead_details.created_at,
                )
            )

        return LeadlistDTO(
            channel_id=None,

            Leaddetails=valid_leads,

            page=page,

            page_size=page_size,

            total=total,

            total_pages=(
                ceil(total / page_size)
                if total > 0
                else 0
            ),
        )

    async def get_lead_channel_identifiers(
            self,
            lead_id: UUID,
            channel_id: UUID,
    ) -> LeadChannelIdentifiersDTO:

        # ==================================================
        # Get Lead
        # ==================================================

        lead = self.lead_repository.get_by_id(
            lead_id
        )

        if lead is None:
            raise ValueError(
                "Lead not found."
            )

        # ==================================================
        # Get connected identifiers for lead's channel
        # ==================================================

        connections = (
            self.channel_connection_repository
            .get_connected_connection(
                user_id=lead.user_id,
                channel_id=channel_id,
            )
        )

        # ==================================================
        # Lead's related identifier first
        # ==================================================

        identifiers = sorted(
            connections,
            key=lambda connection: (
                    connection.id != lead.channel_connection_id
            ),
        )

        # ==================================================
        # Return
        # ==================================================

        return LeadChannelIdentifiersDTO(
            lead_id=lead.id,
            channel_id=channel_id,
            identifiers=[
                ChannelIdentifierDTO(
                    connection_id=connection.id,
                    identifier=connection.provider_identifier,
                    display_name=connection.display_name,
                    is_lead_connection=(
                            connection.id
                            == lead.channel_connection_id
                    ),
                )
                for connection in identifiers
            ],
        )












