"""
BinX AI Chat Client
Simplified client for Discord selfbot integration.
"""

import requests
import json
from typing import Optional, List, Dict, Callable


class BinXChatClient:
    """
    Client for interacting with BinX AI chat API.
    
    Supports:
    - Conversation history management
    - Streaming responses
    """
    
    def __init__(self, auth_token: str):
        """
        Initialize the BinX chat client.
        
        Args:
            auth_token: Bearer token for authentication (format: USERID|TOKEN)
        """
        self.base_url = "https://binx.cc/api/ai-chat"
        self.auth_token = auth_token
        self.conversation_history: List[Dict[str, str]] = []
        self.response_history: List[str] = []
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Origin": "https://binx.cc",
            "Referer": "https://binx.cc/tools/ai-chat",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
            "Sec-GPC": "1",
            "TE": "trailers"
        }
    
    def send_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """
        Send a message to the BinX AI and get the response.
        
        Args:
            message: The message to send to the AI
            conversation_id: Optional conversation ID to maintain context
            stream_callback: Optional callback for streaming response chunks
        
        Returns:
            The full response text or None if error
        """
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Build payload with messages array
        payload = {
            "messages": self.conversation_history
        }
        
        if conversation_id:
            payload["conversationId"] = conversation_id
        
        try:
            # Make the request with streaming enabled
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                raise Exception(error_msg)
            
            # Process the streaming response
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    # SSE format: "data: {json}"
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        # Check for end of stream
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            # Extract content from OpenAI streaming format
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                
                                if 'content' in delta:
                                    content = delta['content']
                                    full_response += content
                                    
                                    # Call streaming callback if provided
                                    if stream_callback:
                                        stream_callback(content)
                        
                        except json.JSONDecodeError:
                            pass
            
            # Add AI response to conversation history
            if full_response:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": full_response
                })
                # Add to response history for reference
                self.response_history.insert(0, full_response)
            
            return full_response
        
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to BinX API. Check your internet connection.")
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error: {str(e)}")
        except KeyboardInterrupt:
            raise KeyboardInterrupt("Response interrupted by user")
    
    def reset_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        self.response_history = []
    
    def get_response_history(self) -> List[str]:
        """Get the list of AI responses (most recent first)."""
        return self.response_history.copy()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        return self.conversation_history.copy()
    
    def set_conversation_history(self, history: List[Dict[str, str]]) -> None:
        """Set the conversation history (useful for restoring sessions)."""
        self.conversation_history = history.copy()

