#!/usr/bin/env python3
"""
Test client for the action-based WebSocket server.
Demonstrates how to use the three main actions:
1. return_conversation
2. store_documents  
3. generate_answer (streaming)
"""

import asyncio
import json
import websockets
from typing import Dict, Any

async def send_action(websocket, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send an action to the WebSocket server and return the response."""
    if data is None:
        data = {}
    
    message = {
        "action": action,
        "data": data
    }
    
    print(f"\n[SENDING] {json.dumps(message, indent=2)}")
    await websocket.send(json.dumps(message))
    
    response = await websocket.recv()
    response_data = json.loads(response)
    action = message["action"]
    print(f"Response for {action} : {response_data} ")
    print(f"[RECEIVED] {json.dumps(response_data, indent=2)}")
    
    return response_data

async def send_streaming_action(websocket, action: str, data: Dict[str, Any] = None):
    """Send a streaming action and handle multiple responses."""
    if data is None:
        data = {}
    
    message = {
        "action": action,
        "data": data
    }
    
    print(f"\n[SENDING STREAMING] {json.dumps(message, indent=2)}")
    await websocket.send(json.dumps(message))
    
    print("\n[STREAMING RESPONSE]:")
    full_response = ""
    chunk_count = 0
    
    while True:
        try:
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "stream_chunk":
                chunk = response_data.get("content", "")
                full_response += chunk
                chunk_count += 1
                # Print chunk immediately without extra formatting
                print(chunk, end="", flush=True)
            elif response_data.get("type") == "stream_complete":
                print(f"\n\n[STREAM COMPLETE] Total chunks received: {chunk_count}")
                print(f"[CONTEXTS] {len(response_data.get('contexts', []))} contexts found")
                print(f"[CONTEXTS] {response_data.get('contexts', [])}")
                break
            elif response_data.get("status") == "error":
                print(f"\n[ERROR] {response_data.get('error', 'Unknown error')}")
                break
            else:
                print(f"\n[UNEXPECTED RESPONSE] {json.dumps(response_data, indent=2)}")
                break
                
        except websockets.exceptions.ConnectionClosed:
            print("\n[CONNECTION CLOSED]")
            break

async def test_websocket_server():
    """Test the WebSocket server with various actions."""
    uri = "ws://localhost:6666"
    #uri = "wss://<ngrok ip address>.ngrok-free.app/" #for exposing the server to the internet
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Test 1: Simple ping test
            print("\n=== Test 1: Ping Test ===")
            await send_action(websocket, "ping")
            
            # Test 2: Generate an answer (streaming)
            print("\n=== Test 2: Generate Answer (Streaming) ===")
            await send_streaming_action(websocket, "generate_answer", {
                "question": "Who is donald trump?"
            })
            
            print("\n=== Test 3: Generate Answer (Streaming) ===")
            await send_streaming_action(websocket, "generate_answer", {
                "question": "Who is his wife?"
            })
            # # Test 5: Generate another answer (streaming)
            # print("\n=== Test 5: Generate Another Answer (Streaming) ===")f
            # await send_streaming_action(websocket, "generate_answer", {
            #     "question": "Explain machine learning in simple terms"
            # })
            
            # Test 6: Return conversation again (should now have both Q&As)
            print("\n=== Test 6: Return Conversation (After Q&As) ===")
            await send_action(websocket, "return_conversation")
            
            # # Test 7: Test invalid action
            # print("\n=== Test 7: Invalid Action ===")
            # await send_action(websocket, "invalid_action")
            
    except websockets.exceptions.ConnectionClosed:
        print("Error: Could not connect to WebSocket server. Make sure the server is running.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("WebSocket Test Client")
    print("Make sure the server is running with: python server.py --api-key YOUR_API_KEY")
    print("=" * 50)
    
    asyncio.run(test_websocket_server()) 