from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catagory, Item
import random
import string

app = Flask(__name__)
engine=create_engine('sqlite:///catalog.db')
Base.metadata.bind=engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/catalog/<int:catalog_id>/item/<int:item_id>')
def Items(catalog_id, item_id):
    item=session.query(Item).filter_by(Id=item_id).one()
    catalog=session.query(Catagory).filter_by(Id=catalog_id).one()
    return render_template('Item.html', item=item, catalog=catalog)

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return "The current session state is %s" % login_session['state']

@app.route('/')
@app.route('/catalog')
def All_catalog():
    catalog= session.query(Catagory).all()
    catagory=[]
    latest=session.query(Item).from_statement(text("SELECT * FROM Item ORDER BY Id ASC LIMIT 2")).all()
    latest=session.query(Item).order_by(Item.Id).limit(2)
    for i in catalog:
        cata_item={}
        cata_item['id']=i.Id
        cata_item['name']=i.name
        items= session.query(Item).filter_by(catagory_id=i.Id).all()
        cata_item['items']=items
        catagory.append(cata_item)
    return render_template('all_catalog.html',catalog=catagory,latest=latest)
    
@app.route('/catalog/<int:catalog_id>')
@app.route('/catalog/<int:catalog_id>/item')
def This_catalog(catalog_id):
    catagory=[]
    catalog= session.query(Catagory).filter_by(Id=catalog_id).one()
    cata_item={}
    cata_item['id']=catalog.Id
    cata_item['name']=catalog.name
    items=session.query(Item).filter_by(catagory_id=catalog.Id).all()
    cata_item['items']=items
    catagory.append(cata_item)
    return render_template('all_catalog.html',catalog=catagory,latest=[])
    
@app.route('/catalog/new', methods=['GET','POST'])
def New_catalog():
    if request.method == 'GET':
        return render_template('new_catalog.html')
    else:
        if request.form['name']:
            newCatagory=Catagory(name=request.form['name'])
            session.add(newCatagory)
            flash("New catagory created!")
            session.commit()
            return redirect(url_for('All_catalog'))
        else:
            flash("Please give a name for catagory")
            return render_template('new_catalog.html')

@app.route('/catalog/<int:catalog_id>/edit', methods=['Get', 'Post'])
def Edit_catalog(catalog_id):
    catagory=session.query(Catagory).filter_by(Id=catalog_id).one()
    if request.method == 'GET':
        return render_template('edit_catalog.html',catagory=catagory)
    else:
        if request.form['name']:
            catagory.name=request.form['name']
            session.add(catagory)
            flash("Catagory modified!")
            session.commit()
            return redirect(url_for('This_catalog', catalog_id=catalog_id))
        else:
            flash("Please give a name to edit the catagory.")
            return render_template('edit_catalog.html',catagory=catagory)
    
@app.route('/catalog/<int:catalog_id>/delete', methods=['GET','POST'])
def Delete_catalog(catalog_id):
    catagory=session.query(Catagory).filter_by(Id=catalog_id).one()
    if request.method == 'GET':
        return render_template('delete_catalog.html',catagory=catagory)
    else:
        item=session.query(Item).filter_by(catagory_id=catalog_id).all()
        session.delete(catagory)
        if item:
            for i in item:
                session.delete(i)
        flash("Catagory and its items deleted!")
        session.commit()
        return redirect(url_for('All_catalog'))

    
@app.route('/catalog/<int:catalog_id>/item/new',  methods=['GET','POST'])
def New_item(catalog_id):
    if request.method == 'GET':
        return render_template('new_item.html', catalog_id=catalog_id)
    else:
        if request.form['name']:
            newItem=Item(name=request.form['name'], attribute=request.form['attribute'],
            description=request.form['description'], url_link=request.form['url'], catagory_id=catalog_id)
            session.add(newItem)
            flash("An item has been created!")
            session.commit()
            return redirect(url_for('This_catalog', catalog_id=catalog_id))
        else:
            flash("Please give a name for item")
            return redirect(url_for('All_catalog'))
        
@app.route('/catalog/<int:catalog_id>/item/<int:item_id>/edit',  methods=['GET','POST'])
def Edit_item(catalog_id, item_id):
    item=session.query(Item).filter_by(Id=item_id).one()
    if request.method == 'GET':
        return render_template('edit_item.html', catalog_id=catalog_id, item=item)
    else:
        if request.form['name']:
            item.name=request.form['name']
            item.attribute=request.form['attribute']
            item.description=request.form['description']
            item.url_link=request.form['url']
            session.add(item)
            flash("An item has been edited!")
            session.commit()
            return redirect(url_for('This_catalog', catalog_id=catalog_id))
        else:
            flash("Please give a name to the edited item.")
            return render_template('edit_item.html', catalog_id=catalog_id, item=item)
            
@app.route('/catalog/<int:catalog_id>/item/<int:item_id>/delete',  methods=['GET','POST'])
def Delete_item(catalog_id, item_id):
    item=session.query(Item).filter_by(Id=item_id).one()
    if request.method == 'GET':
        return render_template('delete_item.html',catalog_id=catalog_id, item=item)
    else:
        session.delete(item)
        flash("An item has been deleted!")
        session.commit()
        return redirect(url_for('This_catalog',catalog_id=catalog_id))
if __name__=='__main__':
    app.secret_key='Alan\'s Key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)