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
        identifier: str,
        lead_details: dict,
    ):
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