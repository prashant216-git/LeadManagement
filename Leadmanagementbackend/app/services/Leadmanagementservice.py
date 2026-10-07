from datetime import datetime, timezone
from math import ceil
from typing import List
from uuid import UUID

from app.DTOs.TransferLeadDTO import TransferLeadResponseDTO
from app.DTOs.ChannelLeadidentifier import LeadChannelIdentifiersDTO, ChannelIdentifierDTO
from app.DTOs.CreateManualLeadDTO import CreateManualLeadDTO
from app.DTOs.Leadlist import LeadlistDTO, Leadetails
from app.enums.channel import ConnectionStatus
from app.models import Lead
from app.core.lock import (
    lead_lock_manager,
)
from app.models.lead_status import LeadStatus
from app.repositories.LeadStatusRepository import LeadStatusRepository
from app.enums.LeadTransfer import LeadTransferStatus, LeadTransferType
from app.models.LeadTransferHistory import LeadTransferHistory
from app.models.lead_status import LeadStatus


class LeadService:

    def __init__(
        self,
        lead_repository,
        channel_connection_repository,
            lead_status_repository,
            lead_status_master_repository,
            status_history_repository,
            lead_transfer_history_repository
    ):
        self.lead_repository = lead_repository
        self.channel_connection_repository = (
            channel_connection_repository
        )
        self.lead_status_repository : LeadStatusRepository =lead_status_repository
        self.lead_status_master_repository=lead_status_master_repository
        self.status_history_repository = status_history_repository
        self.lead_transfer_history_repository=lead_transfer_history_repository

    async def create_or_update_lead(
            self,
            source_channel_id: UUID,
            identifier: str,
            name: str | None = None,
            email: str | None = None,
            phone_number: str | None = None,

    ):


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


            result= self.lead_repository.save(
                lead
            )
            try:
                default_status = (
                    self.lead_status_master_repository
                    .get_by_user_id_default(
                        user_id=connection.user_id
                    )
                )

                if default_status:
                    lead_status = LeadStatus(
                        lead_id=result.id,
                        status_id=default_status.id,
                        update_by=connection.user_id,
                    )

                    self.lead_status_repository.save(lead_status)
                    self.status_history_repository.create(
                        lead_id=result.id,
                        status_id=default_status.id,
                        comment="NEW",
                        changed_by=None,
                    )

            except Exception as exc:
                print(
                    f"Failed to assign status to lead "
                    f"{lead.id}: {exc}"
                )
            return lead


    async def get_lead_by_channel_id(
            self,
            channel_id: UUID,
            page: int = 1,
            page_size: int = 20,
            sort_by: str = "updated_at",
            sort_order: str = "desc",
    ) -> LeadlistDTO:

        offset = (
                         page - 1
                 ) * page_size

        all_leads, total = (
            self.lead_repository
            .get_leads_by_channel_id(
                user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f"),
                channel_id=channel_id,
                limit=page_size,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        )

        default_status = (
            self.lead_status_master_repository
            .get_by_user_id_default(user_id=UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f"))
        )



        valid_leads = []

        for (
                lead_details,
                source_identifier,
                status_name,
            status_updated_at
        ) in all_leads:


            if status_name is None:
                if default_status is not None:
                    lead_status = LeadStatus(
                        lead_id=lead_details.id,
                        status_id=default_status.id,
                        update_by= UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f"),
                    )

                    try:
                        self.lead_status_repository.save(lead_status)

                        status_name = default_status.status_name
                        status_updated_at = lead_status.updated_at

                    except Exception as exc:
                        print(
                            f"Failed to create status for lead "
                            f"{lead_details.id}: {exc}"
                        )





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

                    status =status_name,

                    created_at=(
                        lead_details.created_at
                    ),
                    lead_updated_at=lead_details.updated_at,

                    lead_status_updated_at= status_updated_at ,
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
    ) -> Leadetails:

        lead = None

        # Find existing lead by email
        lead =self.lead_repository.get_by_identifier(user_id=user_id,


                    email=lead_data.email,
                    phone_number=lead_data.phone_number,)

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

            self.lead_repository.save(lead)

            return lead


        lead = Lead(
            user_id=user_id,
            source_channel_id=None,
            name=lead_data.name,
            email=lead_data.email,
            phone_number=lead_data.phone_number,
        )

        result = self.lead_repository.save(
            lead
        )

        try:
            default_status = (
                self.lead_status_master_repository
                .get_by_user_id_default(
                    user_id=user_id
                )
            )

            if default_status:
                lead_status = LeadStatus(
                    lead_id=result.id,
                    status_id=default_status.id,
                    update_by=user_id,
                )
                print("creating lead status")

                self.lead_status_repository.save(lead_status)
                print("creating history")
                self.status_history_repository.create(
                    lead_id=lead.id,
                    status_id=default_status.id,
                    comment="NEW",
                    changed_by=user_id,
                )


        except Exception as exc:
            print(
                f"Failed to assign status to lead "
                f"{lead.id}: {exc}"
            )
        return Leadetails(
            connection_id=None,
            source_identifier=None,
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone_number=lead.phone_number,
            created_at=lead.created_at,
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
                user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f"),
                limit=page_size,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        )
        default_status = (
            self.lead_status_master_repository
            .get_by_user_id_default(user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f"))
        )

        valid_leads = []

        for (lead_details , status,updated_at) in all_leads:

            if status is None:
                if default_status is not None:
                    lead_status = LeadStatus(
                        lead_id=lead_details.id,
                        status_id=default_status.id,
                        update_by= UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f"),
                    )

                    self.lead_status_repository.save(lead_status)

                    status = default_status.status_name

                    updated_at = lead_details.created_at
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

                    status=status,

                    lead_updated_at=lead_details.updated_at,

                    lead_status_updated_at=updated_at,
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

    async def transfer_lead(
            self,
            lead_id: UUID,
            transfer_to: UUID,
            transfer_type: LeadTransferType,
            comment: str,

            current_user_id: UUID,
    ):
        # 1. Get lead
        lead = self.lead_repository.get_by_id(lead_id)

        print("reached srrvice")

        if lead is None:
            raise ValueError("Lead not found.")

        # 2. Current assignee must be the user
        if lead.assigned_user_id != current_user_id:
            raise ValueError(
                "You are not the current assignee of this lead."
            )

        # 3. Cannot transfer to yourself
        if transfer_to == current_user_id:
            raise ValueError(
                "Lead cannot be transferred to yourself."
            )

        # 4. Update current assignee
        lead.assigned_user_id = transfer_to



        # 5. Create transfer history
        transfer_history = LeadTransferHistory(
            lead_id=lead.id,
            transfer_from=current_user_id,
            transfer_to=transfer_to,
            transfer_type=transfer_type,
            transfer_status=LeadTransferStatus.COMPLETED,
            comment=comment,
            created_by=current_user_id,
            updated_by=current_user_id,
        )

        self.lead_transfer_history_repository.create(
            transfer_history
        )
        self.lead_repository.save(lead)
        return lead

    async def get_transfer_history(
            self,
            user_id: UUID,
            transfer_type: str,

            page: int = 1,
            page_size: int = 20,
            sort_by: str = "created_at",
            sort_order: str = "desc",
            channel_id: UUID | None = None,
    ) -> tuple[List[TransferLeadResponseDTO], int]:

        transfers, total = (
            self.lead_transfer_history_repository
            .get_transferred_leads(
                user_id=user_id,
                transfer_type=transfer_type,
                channel_id=channel_id,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        )

        response = []

        for transfer, lead, leadstatus in transfers:
            response.append(
                TransferLeadResponseDTO(
                    id=lead.id,
                    assigned_user_id=lead.assigned_user_id,
                    name=lead.name,
                    email=lead.email,
                    phone_number=lead.phone_number,
                    source_channel_id=lead.source_channel_id,
                    lead_status= leadstatus.status_id,
                    transfer_comment=transfer.comment,
                    created_at=lead.created_at,
                    updated_at=lead.updated_at,
                    transfer_id=transfer.id,
                    transfer_from=transfer.transfer_from,
                    transfer_to=transfer.transfer_to,
                    transfer_type=transfer.transfer_type,
                    transfer_status=transfer.transfer_status,
                    transfer_created_at=transfer.created_at,
                    transfer_updated_at=transfer.updated_at,
                )
            )

        return response, total












