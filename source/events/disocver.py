import time

from events.eventTools import Event, EventRegiseration
from models.Models import Action
from models.Models import PeerSyncResponse, Payload, NodeMetadata
from models.events import InteractionContext
from utils.nodeStorageManager import NodeStorageManager

@EventRegiseration.register
class DiscoverEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.discover.value

    def excute(self, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:



        response = PeerSyncResponse(sender=context.me, connectedPeers=context.nodeManager.nodes, to=sender)
        targetNode = NodeStorageManager.metadataToNodeConnection(sender, context.network.all_nodes)

        context.network.send_to_node(targetNode, {
            "action": Action.syncPeer.value,
            "data": response.model_dump(mode="json")
        })



@EventRegiseration.register
class PeerSyncRsponseEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.syncPeer.value

    def excute(self, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:
        "Responding to the DISCOVER message."

        response = PeerSyncResponse.model_validate(payload.data)

        connections = response.connectedPeers

        for connection in connections:
            host, port = connection.host, connection.port

            isSelf = (context.me.host == host and context.me.port == port)

            already = any(
                n.host == host and n.port == port
                for n in context.network.all_nodes
            )

            if not isSelf and not already:
                context.network.connect_with_node(host=host, port=port)
                time.sleep(0.5)

                if (context.nodeManager.nodeLookup(context.nodeManager.nodes, host, port) in context.nodeManager.nodes):
                    ...

