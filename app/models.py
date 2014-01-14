from app import db

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    openid = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    meta = db.relationship('UserMeta', backref='user', lazy='dynamic')
    # talk = db.relationship('Message', backref='user', lazy='dynamic')
    server = db.Column(db.String(4))
    score = db.Column(db.Integer(), default=0)

    def add_meta(self, name, value):
        if not id:
            raise NameError('This user has not been commited to the db, commit first before adding meta')

        m = UserMeta(name=name, value=value, user=self)
        db.session.add(m)
        db.session.commit()

    def set_meta(self, name, value):
        if not id:
            raise NameError('This user has not been commited to the db, commit first before adding meta')

        q = UserMeta.query.filter_by(user=self, name=name).first()
        if q:
            q.value = value
            db.session.commit()
        else:
            self.add_meta(name, value)

    def get_meta_arr(self, name):
        q = UserMeta.query.filter_by(user=self, name=name).all()
        return q

    def get_meta(self, name):
        q = self.get_meta_arr(name)
        if len(q) > 0:
            return q[0].value
        return None

    def __repr__(self):
        return '<User %r>' % (self.username)


class UserMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    value = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return '<UserMeta %i:%s>' % (self.user_id, self.name)

