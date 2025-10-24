/**
 * WebSocket Service
 * 
 * Handles real-time job updates via WebSocket
 */

import type { JobStatusResponse } from '@/types';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  
  /**
   * Connect to WebSocket for job updates
   */
  connect(
    jobId: string,
    onMessage: (data: JobStatusResponse) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ): void {
    const url = `${WS_BASE_URL}/ws/convert/${jobId}`;
    
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.ws.onmessage = (event) => {
      try {
        const data: JobStatusResponse = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) {
        onError(error);
      }
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket closed');
      
      if (onClose) {
        onClose();
      }
      
      // Attempt reconnection
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => {
          console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
          this.connect(jobId, onMessage, onError, onClose);
        }, this.reconnectDelay * this.reconnectAttempts);
      }
    };
  }
  
  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  /**
   * Send message through WebSocket
   */
  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }
}
