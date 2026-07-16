# API Description

The main way to access the system's functionalities is via API calls. Each path in the system is accessable by API calls. For example:

1. **Block Registeration Path**: To register a block, the user will have to send a POST request to the `/register` end point. The payload that should be sent in the POST request is:

```json

{
    block: Block,
    sender: NodeMetadata
}

```

2. **Ownership Verification Path**: To verify that an identity belongs to a user, the user/authority will have to send a POST requst to the `/verify` end point. The payload that should be sent with the POST request is:

```json
{
    doc: Identity,
    user: User
}
```

```
POST /register
GET /verify
GET /chain
```

