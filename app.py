from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
db = SQLAlchemy(app)

# 데이터베이스 모델 정의
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50))
    birthday = db.Column(db.String(10))
    address = db.Column(db.String(100))
    relation = db.Column(db.String(100))

# 데이터베이스 생성
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    contacts = Contact.query.all()
    return render_template('index.html', contacts=contacts)

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
        
        new_contact = Contact(name=name, phone=phone, email=email, birthday=birthday, address=address, relation=relation)
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



# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)
