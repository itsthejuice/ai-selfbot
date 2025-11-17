"""
BinX AI Chat Client
Simplified client for Discord selfbot integration.
"""

import requests
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Callable

# Configure logger
logger = logging.getLogger('binx_client')
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


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
        logger.info("BinX client initialized")
        logger.debug(f"API endpoint: {self.base_url}")
    
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
        start_time = datetime.now()
        
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        logger.debug(f"Added user message to conversation history (total messages: {len(self.conversation_history)})")
        
        # Build payload with messages array
        payload = {
            "messages": self.conversation_history
        }
        
        if conversation_id:
            payload["conversationId"] = conversation_id
            logger.debug(f"Using conversation ID: {conversation_id}")
        
        try:
            # Make the request with streaming enabled
            logger.info(f"Sending API request to BinX (message length: {len(message)} chars)")
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
                logger.error(f"API request failed: {error_msg}")
                raise Exception(error_msg)
            
            logger.debug("API request successful, starting to stream response...")
            
            # Process the streaming response
            full_response = ""
            chunk_count = 0
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    # SSE format: "data: {json}"
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        # Check for end of stream
                        if data_str.strip() == '[DONE]':
                            logger.debug("Received end-of-stream marker")
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            # Extract content from OpenAI streaming format
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                
                                if 'content' in delta:
                                    content = delta['content']
                                    full_response += content
                                    chunk_count += 1
                                    
                                    # Call streaming callback if provided
                                    if stream_callback:
                                        stream_callback(content)
                        
                        except json.JSONDecodeError as e:
                            logger.debug(f"Failed to parse JSON chunk: {e}")
                            pass
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            # Add AI response to conversation history
            if full_response:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": full_response
                })
                # Add to response history for reference
                self.response_history.insert(0, full_response)
                
                logger.info(f"Response received successfully in {elapsed_time:.2f}s")
                logger.info(f"Response stats: {len(full_response)} chars, {chunk_count} chunks")
                logger.debug(f"Total conversation messages: {len(self.conversation_history)}")
            else:
                logger.warning("Received empty response from API")
            
            return full_response
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: Could not connect to BinX API")
            raise Exception("Could not connect to BinX API. Check your internet connection.")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after 30 seconds")
            raise Exception("Request timed out. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise Exception(f"Request error: {str(e)}")
        except KeyboardInterrupt:
            logger.warning("Response interrupted by user (Ctrl+C)")
            raise KeyboardInterrupt("Response interrupted by user")
    
    def reset_conversation(self) -> None:
        """Clear the conversation history."""
        message_count = len(self.conversation_history)
        self.conversation_history = []
        self.response_history = []
        logger.info(f"Conversation history cleared ({message_count} messages removed)")
    
    def get_response_history(self) -> List[str]:
        """Get the list of AI responses (most recent first)."""
        logger.debug(f"Retrieved response history ({len(self.response_history)} responses)")
        return self.response_history.copy()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        logger.debug(f"Retrieved conversation history ({len(self.conversation_history)} messages)")
        return self.conversation_history.copy()
    
    def set_conversation_history(self, history: List[Dict[str, str]]) -> None:
        """Set the conversation history (useful for restoring sessions)."""
        self.conversation_history = history.copy()
        logger.info(f"Conversation history restored ({len(history)} messages)")

