from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.secret_key = "Hi"
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 데이터베이스 모델 정의
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50))
    birthday = db.Column(db.String(10))
    address = db.Column(db.String(100))
    relation = db.Column(db.String(100))
    image = db.Column(db.String(200))

# 데이터베이스 생성
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    sort_order = request.args.get('sort')  # 정렬 기준 가져오기
    print(f"Received sort_order: {sort_order}")  # 디버깅 출력

    if sort_order == 'name_asc':  # 이름 오름차순 정렬
        contacts = Contact.query.order_by(Contact.name).all()
    elif sort_order == 'name_desc':  # 추가된 순서로 정렬
        contacts = Contact.query.order_by(Contact.id).all()
    else:  # 기본 정렬
        contacts = Contact.query.all()

    print(f"Contacts: {[contact.name for contact in contacts]}")  # 정렬 결과 출력
    return render_template('index.html', contacts=contacts, sort_order=sort_order)



@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        
        email = request.form.get('email')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        relation = request.form.get('relation')
        if relation == '기타':
            relation = request.form.get('custom_relation')
        #image upload
        image_file = request.files.get('image')
        image_filename = None

        if image_file:  # 이미지 파일이 존재할 경우
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = None

        new_contact = Contact(name=name, phone=phone, email=email, birthday=birthday, address=address, relation=relation, image=image_filename)
        db.session.add(new_contact)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_contact.html')

@app.route('/contact/<int:id>')
def detail(id):
    contact = Contact.query.get_or_404(id)
    return render_template('detail.html', contact=contact)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    contact = Contact.query.get_or_404(id)

    if request.method == 'POST':
        # 폼에서 수정된 데이터 가져오기
        contact.name = request.form['name']
        contact.phone = request.form['phone']
        
        contact.email = request.form.get('email')
        contact.birthday = request.form.get('birthday')
        contact.address = request.form.get('address')

        if request.form['relation'] == '기타':
            contact.relation = request.form.get('custom_relation')
        else:
            contact.relation = request.form['relation']        
        
        #image edit
        if 'image' in request.files:
            file = request.files['image']
            filename = secure_filename(file.filename)
        # 파일 저장
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            contact.image = filename  # 이미지 파일 이름을 contact 객체에 저장
        
        
        
        # 데이터베이스에 변경 사항 저장
        db.session.commit()
        return redirect(url_for('detail', id=contact.id))

    return render_template('edit_contact.html', contact=contact)



@app.route('/search')
def search():
    query = request.args.get('query', '')  # 검색어를 받음
    if query:
        # 이름, 전화번호를 기준으로 검색 (대소문자 구분하지 않음)
        contacts = Contact.query.filter(Contact.name.ilike(f'%{query}%') | Contact.phone.ilike(f'%{query}%')).all()
    else:
        contacts = Contact.query.all()  # 검색어가 비었을 경우 모든 연락처 반환
    
    # 결과를 JSON 형식으로 반환
    return jsonify([{
        'id': contact.id,
        'name': contact.name,
        'phone': contact.phone
    } for contact in contacts])




@app.route('/toggle_sort')
def toggle_sort():
    # 정렬 상태를 반전시킴
    sort_by_name = session.get('sort_by_name', False)
    session['sort_by_name'] = not sort_by_name
    return redirect(url_for('index'))  # 변경 후 메인 페이지로 리다이렉트




# 앱 실행



if __name__ == '__main__':
    app.run(debug=True)
