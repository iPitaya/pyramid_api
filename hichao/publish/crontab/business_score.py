from sqlalchemy import (
        Column,
        INTEGER,
        DECIMAL,
        TIMESTAMP,
        func
        )
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import(
        scoped_session,
        sessionmaker,
        )
from zope.sqlalchemy import ZopeTransactionExtension
import logging
from datetime import datetime
import transaction

COMMENT_LIMIT = 10
PROTECT_LIST = [5.0,5.0,5.0]

MYSQL_USER = 'api2'
MYSQL_PASSWD = 'CXxY1KMSm5ewYBnfIqxnOtrMy'
MYSQL_HOST = '192.168.1.108'
MYSQL_PORT = '3306'

MYSQL_SLAVE_USER = 'read'
MYSQL_SLAVE_PASSWD = '8bde2bd~92!749#31_2cd0d2*%9'
MYSQL_SLAVE_HOST = '192.168.1.238'
MYSQL_SLAVE_PORT = '3306'

#MYSQL_USER = 'beta'
#MYSQL_PASSWD = 'f0cf2a92516045024a0c99147b28f05b'
#MYSQL_HOST = '192.168.1.249'
#MYSQL_PORT = '3306'

#MYSQL_SLAVE_USER = 'beta'
#MYSQL_SLAVE_PASSWD = 'f0cf2a92516045024a0c99147b28f05b'
#MYSQL_SLAVE_HOST = '192.168.1.249'
#MYSQL_SLAVE_PORT = '3306'



SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'comment')
SQLALCHEMY_SLAVE_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT, 'comment') 


Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60) 
Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))

rengine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60) 
RDBSession = sessionmaker(bind = rengine)

logfile = 'business_score_info.log'
logger = logging.getLogger()
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def dbsession_generator():
    _DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))
    return _DBSession()

def rdbsession_generator():
    return RDBSession()

class BusinessComment(Base):
    __tablename__ = 'business_comment'

    id = Column('id', INTEGER, primary_key = True, autoincrement = True)
    business_id = Column(INTEGER, nullable=False)
    goods_ratio = Column(TINYINT, nullable = False)
    serve_statisfy = Column(TINYINT, nullable = False)
    logistics_satisfy = Column(TINYINT, nullable = False)
    review = Column(TINYINT, nullable = False)

class BusinessScore(Base):
    __tablename__ = 'business_score'
     
    id = Column('id', INTEGER, primary_key = True, autoincrement = True)
    business_id = Column(INTEGER, nullable=False) 
    goods_score = Column(DECIMAL(10, 1), nullable=False)
    serve_score = Column(DECIMAL(10, 1), nullable=False)
    logistics_score = Column(DECIMAL(10, 1), nullable=False)
    review = Column(TINYINT, nullable = False) 
    create_ts = Column(TIMESTAMP(timezone = False), nullable = False, server_default = func.current_timestamp())
    last_update_ts = Column(TIMESTAMP(timezone = False), nullable = False, server_default = func.current_timestamp())
   
    def __init__(self, business_id, goods_score, serve_score, logistics_score, review, create_ts,last_update_ts):
        self.business_id = business_id
        self.goods_score = goods_score
        self.serve_score = serve_score
        self.logistics_score = logistics_score
        self.review = review
        self.create_ts = create_ts
        self.last_update_ts = last_update_ts

def get_business_scores():
    try:
      RDBSession = rdbsession_generator()
      business_comments = RDBSession.query(BusinessComment.business_id, BusinessComment.goods_ratio, BusinessComment.serve_statisfy, BusinessComment.logistics_satisfy).filter(BusinessComment.review == 1).all()
    except Exception, ex:  
        print Exception, ex
    finally:
        RDBSession.close()
    bcs = [(int(bc[0]), float(bc[1]), float(bc[2]), float(bc[3])) for bc in business_comments]
    business_scores = {}
    business_scores_list = []
    for bc in bcs:
        if bc[0] not in business_scores.keys():
            bs = [bc[1],bc[2],bc[3],1]
            business_scores[bc[0]] = bs
        else:
            bs = business_scores[bc[0]]
            bs_after = [bs[0]+bc[1], bs[1]+bc[2],  bs[2]+bc[3], bs[3]+1]
            business_scores[bc[0]] = bs_after
    for bid, score in business_scores.items():
        bid_score=[]
        bid_score.append(bid)
        if score[3] <= COMMENT_LIMIT:
            score_list = PROTECT_LIST
            #score_list.append(score[3])
        else:
            score_list =[round(score[0]/score[3],1),round(score[1]/score[3],1), round(score[2]/score[3],1)]
        bid_score = bid_score + score_list
        business_scores_list.append(bid_score)
    
    save_business_scores(business_scores_list)
    #f = open('./business_score_statistics.txt', 'w')
    #for bsl in business_scores_list:
        #bsl_str = '   '.join([str(bsl)for bsl in bsl])
        #f.write(bsl_str)
        #f.write("\n")
    #f.close()

def save_business_scores(business_scores_list):
    new_business_list = []
    update_business_list = []
    try:
        RDBSession = rdbsession_generator()
        for bsl in business_scores_list:
            business_id = DBSession.query(BusinessScore.business_id).filter(BusinessScore.business_id == bsl[0]).first()
            if business_id:
                update_business_list.append(bsl)
            else:
                new_business_list.append(bsl)
    except Exception, ex:
        print Exception, ex    
    finally:
        RDBSession.close()
    add_business_scores(new_business_list)
    update_business_scores(update_business_list)

def add_business_scores(new_business_list):
    try:
        new_business_scores = []
        create_ts = datetime.now()
        last_update_ts = datetime.now()
        review = 1
        DBSession = dbsession_generator()
        for nbl in new_business_list:
            business_score = BusinessScore(nbl[0], nbl[1], nbl[2], nbl[3], review, create_ts, last_update_ts)
            new_business_scores.append(business_score)
        DBSession.add_all(new_business_scores)
        transaction.commit()
    except Exception, ex: 
        transaction.abort()
        print Exception, ex
    finally:
        DBSession.close()
    
def update_business_scores(update_business_list):
    try:
        update_business_scores = []
        last_update_ts = datetime.now()
        DBSession = dbsession_generator()
        for ubl in update_business_list:
            update_fileds = {"goods_score": ubl[1], "serve_score":ubl[2], "logistics_score": ubl[3], "last_update_ts": last_update_ts}
            DBSession.query(BusinessScore).filter(BusinessScore.business_id == ubl[0]).update(update_fileds)
        transaction.commit()
    except Exception, ex: 
        transaction.abort()
        print Exception, ex
    finally:
        DBSession.close()

if __name__ == "__main__":
    
    get_business_scores()
