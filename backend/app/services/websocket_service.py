"""
WebSocket Manager for real-time updates
Handles stock updates, notifications, and live data streaming
"""
from typing import List, Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Warehouse-specific subscriptions
        self.warehouse_subscriptions: Dict[int, Set[int]] = {}
        # Product-specific subscriptions
        self.product_subscriptions: Dict[int, Set[int]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        # Clean up subscriptions
        self._cleanup_subscriptions(user_id)
        
    def _cleanup_subscriptions(self, user_id: int):
        """Remove user from all subscriptions"""
        for warehouse_id, users in self.warehouse_subscriptions.items():
            users.discard(user_id)
        for product_id, users in self.product_subscriptions.items():
            users.discard(user_id)
            
    async def subscribe_to_warehouse(self, user_id: int, warehouse_id: int):
        """Subscribe user to warehouse updates"""
        if warehouse_id not in self.warehouse_subscriptions:
            self.warehouse_subscriptions[warehouse_id] = set()
        self.warehouse_subscriptions[warehouse_id].add(user_id)
        
    async def subscribe_to_product(self, user_id: int, product_id: int):
        """Subscribe user to product updates"""
        if product_id not in self.product_subscriptions:
            self.product_subscriptions[product_id] = set()
        self.product_subscriptions[product_id].add(user_id)
        
    async def broadcast_to_user(self, user_id: int, message: dict):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            # Clean up failed connections
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)
                
    async def broadcast_to_warehouse(self, warehouse_id: int, message: dict):
        """Broadcast to all users subscribed to a warehouse"""
        if warehouse_id in self.warehouse_subscriptions:
            for user_id in self.warehouse_subscriptions[warehouse_id]:
                await self.broadcast_to_user(user_id, message)
                
    async def broadcast_to_product(self, product_id: int, message: dict):
        """Broadcast to all users subscribed to a product"""
        if product_id in self.product_subscriptions:
            for user_id in self.product_subscriptions[product_id]:
                await self.broadcast_to_user(user_id, message)
                
    async def broadcast_to_all(self, message: dict):
        """Broadcast to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.broadcast_to_user(user_id, message)


# Global connection manager instance
manager = ConnectionManager()


class StockUpdateNotifier:
    """Handles stock update notifications via WebSocket"""
    
    @staticmethod
    async def notify_stock_change(
        product_id: int,
        warehouse_id: int,
        old_quantity: int,
        new_quantity: int,
        movement_type: str,
        reference_id: int = None
    ):
        """Notify subscribers about stock changes"""
        message = {
            "type": "stock_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "product_id": product_id,
                "warehouse_id": warehouse_id,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "change": new_quantity - old_quantity,
                "movement_type": movement_type,
                "reference_id": reference_id
            }
        }
        
        # Notify warehouse subscribers
        await manager.broadcast_to_warehouse(warehouse_id, message)
        # Notify product subscribers
        await manager.broadcast_to_product(product_id, message)
        
    @staticmethod
    async def notify_low_stock(
        product_id: int,
        product_name: str,
        current_stock: int,
        reorder_point: int
    ):
        """Notify about low stock alerts"""
        message = {
            "type": "low_stock_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "product_id": product_id,
                "product_name": product_name,
                "current_stock": current_stock,
                "reorder_point": reorder_point,
                "severity": "critical" if current_stock == 0 else "warning"
            }
        }
        await manager.broadcast_to_all(message)
        
    @staticmethod
    async def notify_operation_status(
        operation_type: str,  # receipt, delivery, transfer
        operation_id: int,
        old_status: str,
        new_status: str,
        user_id: int = None
    ):
        """Notify about operation status changes"""
        message = {
            "type": "operation_status_change",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "operation_type": operation_type,
                "operation_id": operation_id,
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": user_id
            }
        }
        await manager.broadcast_to_all(message)
