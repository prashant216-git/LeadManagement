from uuid import UUID

from app.DTOs.LeadStatusDTO import LeadStatusResponseDTO
from app.models.lead_status import LeadStatus
from app.models.lead_status_master import LeadStatusMaster
from app.repositories.LeadRepository import LeadRepository
from app.repositories.LeadStatusRepository import LeadStatusRepository
from app.repositories.LeadStatusMasterRepository import (
    LeadStatusMasterRepository,
)


class LeadStatusService:

    def __init__(
        self,
        lead_repository: LeadRepository,
        lead_status_repository: LeadStatusRepository,
        lead_status_master_repository: LeadStatusMasterRepository,
        db,
    ):
        self.lead_repository = lead_repository
        self.lead_status_repository = lead_status_repository
        self.lead_status_master_repository = (
            lead_status_master_repository
        )
        self.db = db

    # --------------------------------------------------
    # GET ALL STATUS
    # --------------------------------------------------

    # async def get_all_statuses(
    #         self,
    #         user_id: UUID,
    # ) -> list[LeadStatusResponseDTO]:
    #
    #     statuses = (
    #         self.lead_status_master_repository
    #         .get_all()
    #     )
    #
    #     return [
    #         LeadStatusResponseDTO.model_validate(status)
    #         for status in statuses
    #     ]

    # --------------------------------------------------
    # GET STATUS BY USER
    # --------------------------------------------------

    async def get_statuses_by_user(
            self,
            user_id: UUID,
    ) -> list[LeadStatusResponseDTO]:

        statuses = (
            self.lead_status_master_repository
            .get_by_user_id(user_id)
        )

        return [
            LeadStatusResponseDTO.model_validate(status)
            for status in statuses
        ]

    # --------------------------------------------------
    # CREATE STATUS
    # --------------------------------------------------

    async def create_status(
        self,
        user_id: UUID,
        status_name: str | None,
        is_active: bool | None,
        is_default: bool | None,
            colour: str | None
    ) -> LeadStatusMaster:

        if not status_name:
            raise ValueError(
                "Status name is required."
            )

        is_active = (
            True
            if is_active is None
            else is_active
        )

        is_default = (
            False
            if is_default is None
            else is_default
        )

        # If new status is default,
        # remove default from existing status.
        if is_default:

            existing_default = (
                self.lead_status_master_repository
                .get_by_user_id_default(user_id)
            )

            if existing_default:
                existing_default.is_default = False

        status = LeadStatusMaster(
            user_id=user_id,
            status_name=status_name,
            is_active=is_active,
            is_default=is_default,
            created_by=user_id,
            colour=colour
        )

        self.lead_status_master_repository.save(
            status
        )

        self.db.commit()
        self.db.refresh(status)

        return status

    # --------------------------------------------------
    # EDIT STATUS
    # --------------------------------------------------

    async def edit_status(
            self,
            user_id: UUID,
            status_id: UUID,
            status_name: str | None,
            is_active: bool | None,
            is_default: bool | None,
    ) -> LeadStatusMaster:

        statuses = (
            self.lead_status_master_repository
            .get_by_user_id(user_id)
        )

        status = next(
            (
                item
                for item in statuses
                if item.id == status_id
            ),
            None,
        )

        if status is None:
            raise ValueError(
                "Lead status not found."
            )

        # ----------------------------------------------
        # Cannot deactivate current default status
        # ----------------------------------------------

        if (
                status.is_default
                and is_active is False
        ):
            raise ValueError(
                "Default status cannot be deactivated."
            )

        # ----------------------------------------------
        # Cannot remove default from current default
        # ----------------------------------------------

        if (
                status.is_default
                and is_default is False
        ):
            raise ValueError(
                "At least one default status is required."
            )

        # ----------------------------------------------
        # Update name
        # ----------------------------------------------

        if status_name is not None:
            status.status_name = status_name

        # ----------------------------------------------
        # Update active
        # ----------------------------------------------

        if is_active is not None:
            status.is_active = is_active

        # ----------------------------------------------
        # Make this status default
        # ----------------------------------------------

        if is_default is True:

            existing_default = (
                self.lead_status_master_repository
                .get_by_user_id_default(user_id)
            )

            if (
                    existing_default
                    and existing_default.id != status.id
            ):
                existing_default.is_default = False

            status.is_default = True

        # ----------------------------------------------
        # Remove default
        # ----------------------------------------------

        elif is_default is False:

            status.is_default = False

        self.db.commit()
        self.db.refresh(status)

        return status

    # --------------------------------------------------
    # DELETE STATUS
    # --------------------------------------------------

    async def delete_status(
        self,
        user_id: UUID,
        status_id: UUID,
    ) -> None:

        statuses = (
            self.lead_status_master_repository
            .get_by_user_id(user_id)
        )
        existing_default=self.lead_status_master_repository.get_by_user_id_default(user_id)
        if existing_default.id == status_id:
            raise ValueError("Default cannot be deleted")

        status = next(
            (
                item
                for item in statuses
                if item.id == status_id
            ),
            None,
        )

        if status is None:
            raise ValueError(
                "Lead status not found."
            )

        self.db.delete(status)
        self.db.commit()

    # --------------------------------------------------
    # CHANGE LEAD STATUS
    # --------------------------------------------------

    async def change_status(
        self,
        user_id: UUID,
        lead_id: UUID,
        status_id: UUID,
    ) -> LeadStatus:



        # ----------------------------------------------
        # Validate Lead
        # ----------------------------------------------

        lead = self.lead_repository.get_by_id(
            lead_id=lead_id
        )

        if lead is None:
            raise ValueError(
                "Lead not found."
            )

        # ----------------------------------------------
        # Validate Status
        # ----------------------------------------------

        statuses = (
            self.lead_status_master_repository
            .get_by_user_id(user_id)
        )

        status = next(
            (
                item
                for item in statuses
                if item.id == status_id
                and item.is_active
            ),
            None,
        )

        if status is None:
            raise ValueError(
                "Lead status not found or inactive."
            )

        # ----------------------------------------------
        # Get Current Status
        # ----------------------------------------------

        lead_statuses = (
            self.lead_status_repository
            .get_by_lead_id(lead_id)
        )

        current_status = (
            lead_statuses[0]
            if lead_statuses
            else None
        )

        # ----------------------------------------------
        # Update Existing
        # ----------------------------------------------

        if current_status:

            current_status.status_id = status_id

            self.db.commit()
            self.db.refresh(current_status)

            return current_status

        # ----------------------------------------------
        # Create
        # ----------------------------------------------

        lead_status = LeadStatus(
            lead_id=lead_id,
            status_id=status_id,
        )

        self.lead_status_repository.save(
            lead_status
        )

        self.db.commit()
        self.db.refresh(lead_status)

        return lead_status