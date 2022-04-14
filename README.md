# CARTO challenge
## Technical decisions
- Defined a port for the database integration and implemented a postgres adapter
- The app's configuration, driven by a .yml file, is motivated as it seems easier to reason about and deploy on Kubernetes clusters
- Separated the "write" side of the app from the "read" side following CQRS. The difference lies in that for read endpoints we rely on services that query DB directly, on the other side, the services that handle the use cases that update the database rely on some other abstractions that also makes easier to test components separately.
- Defined Querying services and "Use Case" services that act as ports to talk to web clients. Current adaptors include the PostgresQueryService and the UsersService
- Decided not to test the DB module that much since in a real scenario one would probably rely on the ORM to at least handle all the connection and trasaction configuration
- The endpoints returning the information needed by the wireframe all execute their own specific query, without allowing for code reuse. Perhaps using an ORM would allow for reusing the same endpoint with filters to group by attributes. Nevertheless, that logic was considered out of the scope of this challenge.

## Potential improvements and considerations
- The database integration could use a HUGE improvement. Namely, using an ORM would render most of the code related to connecting to the DB unnecessary.
- Add support to override configuration defined in `config.yml` through environment variables
- The mechanism to create a test database, inspired by django, could use an improvement.
