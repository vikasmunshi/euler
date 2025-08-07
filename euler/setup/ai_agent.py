#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agentic AI Tool for Project Euler problems."""
from __future__ import annotations

import asyncio
from enum import StrEnum
from typing import Any, cast

from agents import (Agent, AgentOutputSchema, CodeInterpreterTool, ComputerTool, FileSearchTool, FunctionTool,
                    HostedMCPTool, ImageGenerationTool, LocalShellTool, ModelSettings, Runner, WebSearchTool)

from euler.logger import logger


class AgenticModel(StrEnum):
    gpt_4_1 = 'gpt-4.1'
    gpt_4_1_mini = 'gpt-4.1-mini'
    gpt_4_1_nano = 'gpt-4.1-nano'


ToolType = list[FunctionTool | FileSearchTool | WebSearchTool | ComputerTool | HostedMCPTool | LocalShellTool
                | ImageGenerationTool | CodeInterpreterTool]


def agentic_ai_tool[T:Any](agent_input: Any, *,
                           name: str,
                           instructions: str,
                           tools: ToolType,
                           output_type: type[T],
                           model: AgenticModel = AgenticModel.gpt_4_1_mini) -> T:
    async def ai_assistant() -> T:
        agent = Agent(name=name,
                      instructions=instructions,
                      model=str(model),
                      tools=tools,
                      model_settings=ModelSettings(tool_choice='required'),
                      output_type=AgentOutputSchema(output_type, strict_json_schema=False), )
        result = await Runner.run(agent, agent_input)
        return cast(T, result.final_output)

    with asyncio.Runner() as runner:
        agent_output = runner.run(ai_assistant())
    logger.info({'action': name, 'agent_input': agent_input, 'model': str(model), 'result': agent_output})
    return agent_output
