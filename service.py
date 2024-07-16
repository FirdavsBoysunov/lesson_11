from typing import Optional
from session import Session
from db import cursor, conn, commit, is_authenticated
from models import User, UserRole, UserStatus, TodoType
from utils import Response, match_password, hash_password
from validators import check_validation

session = Session()


@commit
def login(username: str, password: str):
    user: User | None = session.check_session()
    if user:
        return Response('You already logged in', 404)
    get_user_by_username = '''
    select * from users where username = %s;
    '''
    cursor.execute(get_user_by_username, (username,))
    user_data = cursor.fetchone()
    if not user_data:
        return Response('User not found', 404)
    user = User.from_tuple(user_data)

    if user.login_try_count >= 3:
        update_status_query = '''update users set status = %s where username = %s;'''
        cursor.execute(update_status_query, (UserStatus.BLOCK.value, username,))
        return Response('User is blocked', status_code=404)

    if not match_password(password, user.password):
        update_user_query = '''
        update users set login_try_count = login_try_count + 1 where username = %s;
        '''
        cursor.execute(update_user_query, (username,))
        return Response('Wrong Password', 404)
    session.add_session(user)
    return Response('User successfully logged in', 200)

@commit
def register_admin(form):
    if check_validation(form):
        return check_validation(form)
    check_user_on_create_query = '''
        select * from users where username = %s;
    '''
    cursor.execute(check_user_on_create_query, (form.username,))
    user_data = cursor.fetchone()
    if user_data:
        return Response('Username already registered', 404)

    register_user_query = '''
    insert into users(username, password, role, status, login_try_count)
    values (%s,%s,%s,%s,%s);
    '''
    data = (form.username, hash_password(form.password), UserRole.ADMIN.value, UserStatus.ACTIVE.value, 0)
    cursor.execute(register_user_query, data)
    return Response('Admin successfully registered', status_code=200)

@commit
def register(form):
    if check_validation(form):
        return check_validation(form)
    check_user_on_create_query = '''
        select * from users where username = %s;
    '''
    cursor.execute(check_user_on_create_query, (form.username,))
    user_data = cursor.fetchone()
    if user_data:
        return Response('Username already registered', 404)

    register_user_query = '''
    insert into users(username, password, role, status, login_try_count)
    values (%s,%s,%s,%s,%s);
    '''
    data = (form.username, hash_password(form.password), UserRole.USER.value, UserStatus.ACTIVE.value, 0)
    cursor.execute(register_user_query, data)
    return Response('User successfully registered', status_code=200)

@is_authenticated
def get_all_users():
    users = [] # databazadan kelgan userlarni saqlab block_user funksiyasiga yuborish uchun ishlatildi
    get_all_users_query = '''SELECT id, username, status FROM users WHERE role = 'user';'''
    cursor.execute(get_all_users_query)
    users_data = cursor.fetchall()
    if not users_data:
        return Response('There are no users in the database yet' ,404)
    for user in users_data:
        users.append(user)
    return users


@is_authenticated
@commit
def user_block(user_id: int):
    role = session.session.role
    if role != 'admin':# userlar faqat adminlar tomonidan blocklansa bo'ladigan qilingan
        return Response('You must be an admin to block', 404)
    users_data = get_all_users()
    for user in users_data:
        if user_id in str(user):
            block_user_query = '''UPDATE users SET status = %s, login_try_count = 3 WHERE id = %s;'''
            cursor.execute(block_user_query,(UserStatus.BLOCK.value,user_id,))
            return Response('Successfully blocked', 200)
    return Response('User not found' ,404)

    
    
    pass

def logout():
    global session
    if session:
        session.session = None
        return Response('Successfully logged out', status_code=200)
    return Response('Session Not Found', status_code=404)

@is_authenticated
def get_all_todos():
    todos = [] 
    get_all_todos_query = '''SELECT id, name FROM todo WHERE user_id = %s;'''
    cursor.execute(get_all_todos_query,(session.session.id,))
    todo_list = cursor.fetchall()
    if not todo_list:
        return Response('You do not have any todo', 404)
    for todo in todo_list:
        todos.append(todo)
    return todos
    
@is_authenticated
@commit
def todo_add(name: str, description: Optional[str] = None):
    insert_todo = """
        insert into todo(name,description,todo_type,user_id)
        values (%s,%s,%s,%s)
    """
    cursor.execute(insert_todo, (name, description, TodoType.PERSONAL.value, session.session.id))
    return Response('Successfully inserted todo', status_code=200)
    
@commit
def todo_update(name: str, todo_id: int, description: Optional[str] = None):
    todos = get_all_todos()
    for todo in todos:
        if todo_id in str(todo): 
            update_todo_query = '''UPDATE todo SET name = %s, 
                                    description = %s WHERE id = %s;'''
            cursor.execute(update_todo_query,(name, description, todo_id))
            return Response('Successfully updated todo', 200)
    return Response(f'You do not have todo with that id {todo_id}', 404)

@commit
def  todo_delete(todo_id: str):
    todos = get_all_todos()
    for todo in todos:
        if todo_id in str(todo):
            delete_todo_query = '''DELETE FROM todo WHERE id = %s;'''
            cursor.execute(delete_todo_query,(todo_id,))
            return Response('Successfully deleted todo', 200)
    return Response(f'You do not have todo with that id {todo_id}', 404)