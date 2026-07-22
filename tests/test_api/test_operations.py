from decimal import Decimal

from app.models import User, Wallet


def test_add_expense_success(db_session, client):
    # Arrange
    user = User(login='test')
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id = user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    
    # Act
    response = client.post(
        '/api/v1/operations/expense', 
        json={
            'wallet_name': 'card',
            'amount': 50.0,
            'description': 'Food'
        },
        headers={'Authorization': f"Bearer {user.login}"}
        )
    
    # Assert
    assert response.status_code == 200
    assert response.json()['message'] == 'Расход добавлен'
    assert response.json()['wallet'] == 'card'
    assert Decimal(str(response.json()['amount'])) == Decimal(50.0)
    assert response.json()['description'] == 'Food'
    assert Decimal(str(response.json()['new_balance'])) == Decimal(150.0)
    
    
def test_add_negative_amount_failure_422(db_session, client):
    # Arrange
    user = User(login='test')
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id = user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    
    # Act
    response = client.post(
        '/api/v1/operations/expense', 
        json={
            'wallet_name': 'card',
            'amount': -50.0,
            'description': 'Food'
        },
        headers={'Authorization': f"Bearer {user.login}"}
        )
    
    # Assert
    assert response.status_code == 422

 
def test_add_expense_empty_name_failure_422(db_session, client):
    # Arrange
    user = User(login='test')
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id = user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    
    # Act
    response = client.post(
        '/api/v1/operations/expense', 
        json={
            'wallet_name': '   ',
            'amount': 50.0,
            'description': 'Food'
        },
        headers={'Authorization': f"Bearer {user.login}"}
        )
    
    # Assert
    assert response.status_code == 422
    

def test_add_expense_wallet_not_exists_failure_404(db_session, client):
    # Arrange
    user = User(login='test')
    db_session.add(user)
    db_session.flush()
    db_session.commit()
    
    # Act
    response = client.post(
        '/api/v1/operations/expense', 
        json={
            'wallet_name': 'не_существующий_кошелек',
            'amount': 50.0,
            'description': 'Food'
        },
        headers={'Authorization': f"Bearer {user.login}"}
        )
    
    # Assert
    assert response.status_code == 404
    

def test_add_expense_unauthorized_failure_401(client): 
    # Arrange
    
    # Act
    response = client.post(
        '/api/v1/operations/expense', 
        json={
            'wallet_name': 'card',
            'amount': 50.0,
            'description': 'Food'
        },
        headers={'Authorization': f"Bearer notexists"}
        )
    
    # Assert
    assert response.status_code == 401
    
    
def test_add_expense_not_enought_money_failure_400(db_session, client):
    # Arrange
    user = User(login='test')
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id = user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    
    # Act
    response = client.post(
        '/api/v1/operations/expense', 
        json={
            'wallet_name': 'card',
            'amount': 500.0,
            'description': 'Food'
        },
        headers={'Authorization': f"Bearer {user.login}"}
        )
    
    # Assert
    assert response.status_code == 400
