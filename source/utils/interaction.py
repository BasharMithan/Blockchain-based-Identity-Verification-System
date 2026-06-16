import json

from source.models.Models import Block, Action, Response
from source.models.Models import Qwery as Query
from source.utils.logger import Logger
from source.services.blockManager import BlockManager
from source.services.verifier import Verifier

from source.errors import DuplicateBlockError, InvalidBlockPayloadError, InvalidChainError, BlockHashMismatchError, BlockNotMinedError, BlockPreviousHashError



class HandleIncomingInteraction:
    def __init__(self, interaction: dict, blockManager: BlockManager, seenBlocks: set) -> None:
        self.blockManager = blockManager
        self.interaction = interaction
        self.seenBlocks: set = seenBlocks
        Logger.info(f"[Interaction - init] Got an interaction...")
        print(self.blockManager.ledger.filePath)

    def getAsBlock(self) -> Block | None:
        if self.extractAction() in (Action.registeration.value, Action.BlockBroadcast.value):
            blockDict = self.interaction.get("data")
            if isinstance(blockDict, str):
                try:
                    blockDict = json.loads(blockDict)
                except json.JSONDecodeError:
                    return None
            return Block.model_validate(blockDict)
        return None
        


    def extractAction(self) -> str:
         return self.interaction.get("action") # type: ignore
         
    
    def shouldBroadcast(self) -> bool:

        possibleBlock = self.__classifyInteraction()

        if isinstance(possibleBlock, Block):

            if (possibleBlock.data.chid in self.seenBlocks):
                Logger.info(f"[Interaction] Block {possibleBlock.data.user.name} should not be broadcasted.")
                return False

            else:
                Logger.info(f"[Interaction] Block {possibleBlock.data.user.name} should be broadcasted.")
                self.seenBlocks.add(possibleBlock.data.chid)
                return True 
            


        Logger.warning(f"[Interaction - Broadcast checking] Invalid block.")
        return False
         

        

    def handle(self) -> None:
        """Handles the incoming interaction detected in the `node_message` function"""
        Logger.info(f"[Interaction] Starting the interaction handler.")

        decision: Block | Query | None = self.__classifyInteraction()

        if (isinstance(decision, Block)):

            self.__handleBlockInteraction(decision)

        elif (isinstance(decision, Query)):
            self.__handleQueryInteraction(decision) 



    def __handleBlockInteraction(self, block: Block) -> None:
        """Handles the received block"""


        try:
                self.blockManager.receiveBlock(block)

        except InvalidBlockPayloadError as error:
                Logger.warning(f"[Peer] Invalid block payload: {str(error)}")

        except (
                BlockNotMinedError, DuplicateBlockError, BlockPreviousHashError,
                BlockHashMismatchError) as error:
                Logger.warning(f"[Interaction] Block validation failed: {str(error)}")


        except InvalidChainError as error:
            Logger.warning(f"[Interaction] Chain validation failed: {str(error)}")


    def __handleQueryInteraction(self, query: Query) -> Response:
        """Handles the incoming queris"""
        response: Response = Verifier.check(query)
        return response

    def __handleBlockBroadcast(self, block: Block, sender: str) -> None:
        self.__handleBlockInteraction(block)


    def __classifyInteraction(self) -> Block | Query | None:
        """Takes the incoming interaction and returns it's proper type (Block or Query)"""

        action: str = self.extractAction()
        
        data = self.interaction.get("data")
        sender = self.interaction.get("sender", None)

        if (action not in Action.getactionsaslist()):
            Logger.warning(f"[Interaction] Unknown action: got: {action}, available actions: {Action.getactionsaslist()}")
            return None


        print(f"[Interaction] got: {action}")

        if action == Action.registeration.value:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return None
            return Block.model_validate(data)

        if action == Action.BlockBroadcast.value:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return None
            return Block.model_validate(data)

        if action == Action.query.value:
            return Query.model_validate(data)

        return None 
