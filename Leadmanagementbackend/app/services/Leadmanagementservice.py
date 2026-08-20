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

            await self.lead_repository.update(lead)

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

        """
        Create or update a lead using an external
        channel identifier.

        The tenant is resolved internally from the
        identifier.
        """

        # ---------------------------------------------
        # 1. Resolve tenant + connection
        # ---------------------------------------------

        connection = await (
            self.channel_connection_repository
            .get_by_provider_identifier(
                identifier=identifier
            )
        )

        if connection is None:
            raise ValueError(
                "No channel connection found "
                "for this identifier."
            )

        tenant_id = connection.tenant_id

        # ---------------------------------------------
        # 2. Find existing lead
        # ---------------------------------------------

        lead = await (
            self.lead_repository
            .get_by_identifier(
                tenant_id=tenant_id,
                identifier=identifier,
            )
        )

        # ---------------------------------------------
        # 3. Create
        # ---------------------------------------------

        if lead is None:

            lead = Lead(
                tenant_id=tenant_id,
                name=lead_details.get("name"),
                email=lead_details.get("email"),
                phone_number=lead_details.get(
                    "phone_number"
                ),
                summary=lead_details.get(
                    "summary"
                ),
            )

            return await self.lead_repository.save(
                lead
            )

        # ---------------------------------------------
        # 4. Update
        # ---------------------------------------------

        for field in (
            "name",
            "email",
            "phone_number",
            "summary",
        ):
            value = lead_details.get(field)

            if value is not None:
                setattr(
                    lead,
                    field,
                    value,
                )

        return await self.lead_repository.save(
            lead
        )