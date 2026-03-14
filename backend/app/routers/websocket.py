"""
WebSocket Router for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database.connection import get_db
from app.services import auth_service, websocket_service
from app.services.websocket_service import manager, StockUpdateNotifier
from app.models.models import User

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/stock")
async def websocket_stock_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time stock updates
    
    Connection URL: ws://localhost:8000/ws/stock?token=<JWT_TOKEN>
    
    Messages:
    - Subscribe to warehouse: {"action": "subscribe_warehouse", "warehouse_id": 1}
    - Subscribe to product: {"action": "subscribe_product", "product_id": 1}
    - Ping: {"action": "ping"}
    """
    # Verify JWT token
    payload = auth_service.verify_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    
    user_id = int(payload.get("sub"))
    
    # Accept connection
    await manager.connect(websocket, user_id)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to CoreInventory real-time updates",
            "user_id": user_id
        })
        
        while True:
            # Receive and process messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe_warehouse":
                    warehouse_id = message.get("warehouse_id")
                    if warehouse_id:
                        await manager.subscribe_to_warehouse(user_id, warehouse_id)
                        await websocket.send_json({
                            "type": "subscription_confirmed",
                            "subscription": "warehouse",
                            "warehouse_id": warehouse_id
                        })
                        
                elif action == "subscribe_product":
                    product_id = message.get("product_id")
                    if product_id:
                        await manager.subscribe_to_product(user_id, product_id)
                        await websocket.send_json({
                            "type": "subscription_confirmed",
                            "subscription": "product",
                            "product_id": product_id
                        })
                        
                elif action == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": websocket_service.datetime.utcnow().isoformat()
                    })
                    
                elif action == "unsubscribe_warehouse":
                    warehouse_id = message.get("warehouse_id")
                    if warehouse_id and warehouse_id in manager.warehouse_subscriptions:
                        manager.warehouse_subscriptions[warehouse_id].discard(user_id)
                        await websocket.send_json({
                            "type": "unsubscription_confirmed",
                            "subscription": "warehouse",
                            "warehouse_id": warehouse_id
                        })
                        
                elif action == "unsubscribe_product":
                    product_id = message.get("product_id")
                    if product_id and product_id in manager.product_subscriptions:
                        manager.product_subscriptions[product_id].discard(user_id)
                        await websocket.send_json({
                            "type": "unsubscription_confirmed",
                            "subscription": "product",
                            "product_id": product_id
                        })
                        
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        raise


@router.websocket("/dashboard")
async def websocket_dashboard_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for dashboard real-time KPI updates
    
    Connection URL: ws://localhost:8000/ws/dashboard?token=<JWT_TOKEN>
    
    Receives automatic updates for:
    - Stock level changes
    - Low stock alerts
    - Operation status changes
    """
    # Verify JWT token
    payload = auth_service.verify_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    
    user_id = int(payload.get("sub"))
    
    # Accept connection
    await manager.connect(websocket, user_id)
    
    try:
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to dashboard updates",
            "user_id": user_id
        })
        
        # Keep connection alive and handle pings
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": websocket_service.datetime.utcnow().isoformat()
                    })
                    
            except json.JSONDecodeError:
                pass  # Ignore invalid messages, just keep connection alive
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        raise
