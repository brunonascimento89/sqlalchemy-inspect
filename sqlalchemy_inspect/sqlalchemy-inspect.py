import os
from sqlalchemy import create_engine, inspect


def capitalize_strings(string):
    string_str = ''
    for name in string.split('_'):
        if not string_str: string_str = name.capitalize()
        else: string_str = string_str + name.capitalize()
    return string_str


class MySQLdb:

    def __init__ (self, host, port, database, user, password, filename, engine_args=False):
        '''
        host: server host\n
        port: server port\n
        database: database name or database ip address\n
        user: username of database\n
        password: password of database\n
        filename: name of SQLAlchemy model\n
        engine_args: insert arguments in engine. Default=False\n
        '''
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.filename = filename
        self.engine_args = engine_args

    def extract_model(cls):
        '''
        Create SQLAlchemy Model
        '''
        try:
            engine = create_engine('{engine}://{user}:{password}@{host}:{port}/{name}'.format(
                engine='mysql+pymysql', user=cls.user, password=cls.password, host=cls.host, port=cls.port, name=cls.database,
            ))
        except Exception as e:
            raise Exception(f'Something goes wrong with \'{cls.host}\' database. Error : {e}')
        else:
            try:
                inspector = inspect(engine)
            except Exception as e:
                raise Exception(e)
        
        with open(os.path.join(os.getcwd(), f'{cls.filename}'), 'w') as f:
            f.write("from sqlalchemy import create_engine, Column, BigInteger, SmallInteger, Float, String, Integer, Date, TIMESTAMP, DateTime, Text, ForeignKey\n")
            f.write("from sqlalchemy.ext.declarative import  declarative_base\n")
            f.write("from sqlalchemy.orm import relationship\n\n")

            f.write("from datetime import datetime\n\n")

            f.write("from decouple import config\n\n")

            if cls.engine_args:
                f.write("engine = create_engine('mysql+pymysql://{creds}:{creds}@{creds}:{creds}/{creds}' % (config('DB_USER'), config('DB_PASS'), config('DB_HOST'), config('DB_PORT'), config('DB_NAME')))\n".format(creds="%s"))
            else:
                f.write("engine = create_engine('mysql+pymysql://')\n")

            f.write("base = declarative_base(bind=engine)\n\n\n")

            for table_name in inspector.get_table_names():

                f.write("class {class_name}(base):\n\n".format(class_name=capitalize_strings(table_name)))
                f.write("\t__tablename__ = '{tablename}'\n\n".format(tablename=table_name))
                relationship_list = []
                columns_list = []
                for params in inspector.get_columns(table_name):
                    columns_list.append(params['name'])
                    params_aux = list(params.keys())
                    params_aux.remove('name'); params_aux.remove('type')

                    ########################
                    # col_name = Column(Datatype
                    ########################
                    # Timestamp datatype: SQLALCHEMY TIMESTAMP
                    if str(params['type']).lower() == 'timestamp': column_str = "{datatype} = Column(TIMESTAMP".format(datatype=params['name'])
                    # Datetime datatype: SQLALCHEMY DateTime
                    elif str(params['type']).lower() == 'datetime': column_str = "{datatype} = Column(DateTime".format(datatype=params['name'])
                    # Bigint datatype: SQLALCHEMY BigInteger
                    elif str(params['type']).lower() == 'bigint': column_str = "{datatype} = Column(BigInteger".format(datatype=params['name'])
                    # Tinyint datatype: SQLALCHEMY SmallInteger
                    elif str(params['type']).lower() == 'tinyint' or str(params['type']).lower() == 'smallint': column_str = "{datatype} = Column(SmallInteger".format(datatype=params['name'])

                    else:
                        # Varchar(255) datatype: SQLALCHEMY String(255)
                        if 'varchar' in str(params['type']).lower(): params['type'] = (str(params['type']).lower()).replace('varchar', 'String')
                        # Char(2) datatype: SQLALCHEMY String(2)
                        elif 'char' in str(params['type']).lower(): params['type'] = (str(params['type']).lower()).replace('char', 'String')
                        # Longtext datatype: SQLALCHEMY Text
                        elif 'longtext' in str(params['type']).lower(): params['type'] = (str(params['type']).lower()).replace('longtext', 'Text')
                        # Double datatype: SQLALCHEMY Float
                        elif 'double' in str(params['type']).lower(): params['type'] = (str(params['type']).lower()).replace('double', 'Float')
                        # Rest of datatypes just get the raw name
                        # column_str = "%s = Column(%s" % (params['name'], str(params['type']).capitalize())
                        column_str = "%s = Column(%s" % (params['name'], capitalize_strings(str(params['type'])))

                    ########################
                    # Get primary key
                    ########################
                    for primary_key in inspector.get_pk_constraint(table_name)['constrained_columns']:
                        if primary_key == params['name']: column_str = column_str + ", primary_key=True"
                    ########################
                    # ForeignKey(class_name.column, onupdate="something", ondelete="NO ACTION") 
                    ########################
                    foreign_key = None
                    for foreign_key in inspector.get_foreign_keys(table_name):
                        if foreign_key['constrained_columns'][0] == params['name']: break
                        else: foreign_key = None
                    if foreign_key:
                        # Build the foreign_key configuration
                        if foreign_key['options']:
                            column_str = column_str + ", ForeignKey(\"%s.%s\", onupdate=\"%s\", ondelete=\"NO ACTION\")" % (
                                foreign_key['referred_table'], foreign_key['referred_columns'][0], foreign_key['options']['onupdate']
                            )
                        else:
                            column_str = column_str + ", ForeignKey(\"%s.%s\")" % (
                                foreign_key['referred_table'], foreign_key['referred_columns'][0]
                            )
                        # Build the relationship configuration
                        # Add primaryjoin agument to take a reference of primary key
                        relationship_list.append("{relation_col} = relationship(\"{relation_table}\")".format(
                            relation_col=str(foreign_key['constrained_columns'][0]).replace('_id', ''), relation_table=capitalize_strings(foreign_key['referred_table'])
                        ))
                        
                    ########################
                    # Column parameters
                    ########################
                    for param in params_aux:
                        # if on update exist in argument, will save default=datetime.utcnow(), onupdate=datetime.utcnow()
                        if 'on update' in str(params[param]).lower():
                            
                            # Filter for onupdate column settings
                            onupdate_list = str(params[param]).lower().split('on update')
                            for idx, value in enumerate(onupdate_list):
                                if value.strip() == 'current_timestamp()':
                                    onupdate_list[idx] = 'datetime.utcnow()'
                                else:
                                    onupdate_list[idx] = value
                            params[param] = "{default_val}, onupdate={onupdate_val}".format(default_val=onupdate_list[0], onupdate_val=onupdate_list[1])

                        elif not 'on update' in str(params[param]).lower():
                            # if on update not exist in argument and current_timestamp() exists, it will save default=datetime.utcnow()
                            if 'current_timestamp()' in str(params[param]).lower():
                                params[param] = 'datetime.utcnow()'
                        
                        column_str = column_str + ', {param_arg}={param_val}'.format(param_arg=param, param_val=params[param])
                    column_str = column_str + ')'
                    f.write("\t{column_str}\n".format(column_str=column_str))

                if relationship_list:
                    # Insert the relationship configuration
                    f.write("\n")
                    for relationship_str in relationship_list:
                        f.write("\t{relation_str}\n".format(relation_str=relationship_str))

                ########################
                # def __repr__(self): return <var1=self.var1, var2=self.var2>
                ########################
                return_str = None
                for column in columns_list:
                    if not return_str:
                        return_str = "f'<%(0)s={self.%(0)s}" % ({'0': column})
                    else:
                        return_str += ", %(0)s={self.%(0)s}" % ({'0': column})
                
                if return_str:
                    f.write("\n\tdef __repr__(self):\n")
                    return_str += ">'"
                    f.write("\t\treturn {repr_args}\n".format(repr_args=return_str))

                f.write("\n\n")

            f.write("base.metadata.create_all(engine, checkfirst=True) # Create the table if not exist")
