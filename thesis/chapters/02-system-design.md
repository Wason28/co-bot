# Chapter 2 - System Design

Use this chapter to describe the frozen architecture and the non-negotiable
semantics:

- dual-camera perception
- Supervisor / Social / Action split
- policy gate and confirmation flow
- checkpoint plus long-term memory

## M1 verification hooks

- robot control evidence contract: `services/robot-mcp/tool_manifest.json`
- dual-camera evidence contract: `services/perception/camera_contract.json`
- real-risk integration manifest: `services/device_integration_manifest.json`
