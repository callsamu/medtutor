from collections.abc import Mapping
from typing import Any, Optional

from classifier import BaseClassifier
from langchain.chains.base import Chain
from langchain.callbacks.manager import CallbackManagerForChainRun


class ClassifyRouterChain(Chain):
    classifier: BaseClassifier
    destination_chains: Mapping[str, Chain]
    default_chain: Chain
    raise_error = False

    routing_key = "input"

    @property
    def input_keys(self) -> list[str]:
        return [self.routing_key]

    @property
    def output_keys(self) -> list[str]:
        return []

    def _call(
        self,
        inputs: dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> dict[str, Any]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()

        callbacks = _run_manager.get_child()
        _input = inputs[self.routing_key]
        destination = self.classifier.classify(_input)

        chain = self.default_chain
        if destination not in self.destination_chains:
            if self.raise_error:
                message = "Received invalid destination chain name "
                message += f"'{destination}'"
                raise ValueError(message)
        else:
            chain = self.destination_chains[destination]

        for key in chain.input_keys:
            if key not in inputs:
                inputs[key] = _input

        return chain(inputs, callbacks=callbacks)
