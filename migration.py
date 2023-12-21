from datetime import datetime
from alembic import op
import sqlalchemy as sa

from models.classes import Categories, Conclusions, Regions, Statuses
from models.schema import DocumentSchema, PersonSchema, StaffSchema, PathSchema, \
    RegAddressSchema, LiveAddressSchema, PhoneContactSchema, EmailContactSchema


def upgrade_db():
    conn = op.get_bind()
    
    categories = op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, 
                  unique=True, nullable=False),
        sa.Column('category', sa.String(255))
    )
    op.bulk_insert(categories, [{'category': item.value} for item in Categories])

    statuses = op.create_table(
        'statuses',
        sa.Column('id', sa.Integer(), primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('status', sa.String(255))
    )
    op.bulk_insert(statuses, [{'status': item.value} for item in Statuses])
    
    regions = op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('region', sa.String(255))
    )
    op.bulk_insert(regions, [{'region': item.value} for item in Regions])

    conclusions = op.create_table(
        'conclusions',
        sa.Column('id', sa.Integer(), primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('conclusion', sa.String(255))
    )
    op.bulk_insert(conclusions, [{'conclusion': item.value} for item in Conclusions])

    staffs = op.create_table(
        'staffs',
        sa.Column('id', sa.Integer(), primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('position', sa.Text()),
        sa.Column('department', sa.Text()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    res = conn.execute(sa.text(
        "SELECT id, staff, department FROM persons"
    ))
    results = res.fetchall()
    op.bulk_insert(staffs, StaffSchema().dump(results, many=True))

    documents = op.create_table(
        'documents',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('series', sa.String(255)),
        sa.Column('number', sa.String(255)),
        sa.Column('agency', sa.Text()),
        sa.Column('issue', sa.Date()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    res = conn.execute(sa.text(
        "SELECT id, series_passport, number_passport, date_given FROM persons"
    ))
    results = res.fetchall()
    op.bulk_insert(documents, DocumentSchema().dump(results, many=True))
    
    addresses = op.create_table(
        'addresses',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('region', sa.String(255)),
        sa.Column('address', sa.Text()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    res_reg = conn.execute(sa.text(
        "SELECT id, reg_address FROM persons"
    ))
    res_live = conn.execute(sa.text(
        "SELECT id, live_address FROM persons"
    ))
    op.bulk_insert(addresses, RegAddressSchema().dump(res_reg.fetchall(), many=True) 
                   + LiveAddressSchema().dump(res_live.fetchall(), many=True))
    
    contacts = op.create_table(
        'contacts',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('contact', sa.String(255)),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    res_phone = conn.execute(sa.text(
        "SELECT id, phone FROM persons"
    ))
    res_mail = conn.execute(sa.text(
        "SELECT id, email FROM persons"
    ))
    results = res.fetchall()
    op.bulk_insert(contacts, PhoneContactSchema().dump(res_phone.fetchall(), many=True) 
                   + EmailContactSchema().dump(res_mail.fetchall(), many=True))    
    op.create_table(
        'workplaces',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('start_date', sa.Date()),
        sa.Column('end_date', sa.Date()),
        sa.Column('workplace', sa.String(255)),
        sa.Column('address', sa.Text()),
        sa.Column('position', sa.Text()),
        sa.Column('reason', sa.Text()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )

    op.create_table(
        'affilations',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('name', sa.Text()),
        sa.Column('inn', sa.String(255)),
        sa.Column('position', sa.Text()),
        sa.Column('deadline', sa.Date()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )

    op.create_table(
        'robots',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('employee', sa.Text()),
        sa.Column('inn', sa.Text()),
        sa.Column('bankruptcy', sa.Text()),
        sa.Column('bki', sa.Text()),
        sa.Column('courts', sa.Text()),
        sa.Column('terrorist', sa.Text()),
        sa.Column('mvd', sa.Text()),
        sa.Column('deadline', sa.Date()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )

    op.create_table(
        'connects',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('company', sa.String(255)),
        sa.Column('city', sa.String(255)),
        sa.Column('fullname', sa.String(255)),
        sa.Column('phone', sa.String(255)),
        sa.Column('adding', sa.String(255)),
        sa.Column('mobile', sa.String(255)),
        sa.Column('mail', sa.String(255)),
        sa.Column('comment', sa.Text()),
        sa.Column('data', sa.Date()),
    )

    persons = op.create_table(
        'persons',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('region_id', sa.Integer(), 
                  sa.ForeignKey('regions.id',
                                name='fk_persons_region_id')),
        sa.Column('category_id', sa.Integer(), 
                  sa.ForeignKey('categories.id',
                                name='fk_persons_category_id')),
        sa.Column('fullname', sa.String(255)),
        sa.Column('previous', sa.Text()),
        sa.Column('birthday', sa.Date()),
        sa.Column('birthplace', sa.Text()),
        sa.Column('country', sa.String()),
        sa.Column('ext_country', sa.Text()),
        sa.Column('snils', sa.String()),
        sa.Column('inn', sa.String()),
        sa.Column('education', sa.Text()),
        sa.Column('marital', sa.String()),
        sa.Column('addition', sa.Text()),
        sa.Column('path', sa.Text()),
        sa.Column('status_id', sa.Integer(), 
                  sa.ForeignKey('statuses.id',
                                name='fk_persons_status_id')),
        sa.Column('create', sa.Date()),
        sa.Column('update', sa.Date())
    )
    res = conn.execute(sa.text(
        "SELECT id, full_name, last_name, birthday, birth_place, country, snils, inn, education FROM persons"
    ))
    results = res.fetchall()
    op.bulk_insert(persons, PersonSchema().dump(results, many=True))

    # migrate check table
    with op.batch_alter_table('checks') as batch_op:
        batch_op.alter_column('check_work_place', 
                              new_column_name='workplace')
        batch_op.alter_column('check_passport', 
                              new_column_name='document')
        batch_op.alter_column('check_debt', 
                              new_column_name='debt')
        batch_op.alter_column('check_bankruptcy', 
                              new_column_name='bankruptcy')
        batch_op.alter_column('check_bki', 
                              new_column_name='bki')
        batch_op.alter_column('check_affiliation', 
                              new_column_name='affiliation')
        batch_op.alter_column('check_internet', 
                              new_column_name='internet')
        batch_op.alter_column('check_work_place', 
                              new_column_name='workplace')
        batch_op.alter_column('check_cronos', 
                              new_column_name='cronos')
        batch_op.alter_column('check_cross', 
                              new_column_name='cros')
        batch_op.alter_column('officer', 
                              type_=sa.String(255), 
                              existing_type=sa.Text())
        batch_op.alter_column('date_check', 
                              new_column_name='deadline', 
                              type_=sa.Date(), 
                              existing_type=sa.Text())
        batch_op.alter_column('check_id', 
                              new_column_name='person_id')

        batch_op.add_column(sa.Column('comments', sa.Text()))
        batch_op.add_column(sa.Column('pfo', sa.Boolean()))
        batch_op.add_column(sa.Column('addition', sa.Text()))
        batch_op.add_column(sa.Column('conclusion_id', sa.Integer(), 
                                      sa.ForeignKey('conclusions.id',
                                                    name='fk_checks_conclusion_id')))
        batch_op.drop_column('resume')

    ###
    op.rename_table('iqueries', 'inquiries')
    with op.batch_alter_table('inquiries') as batch_op:
        batch_op.add_column(sa.Column('source', sa.String(255)))
        batch_op.add_column(sa.Column('officer', sa.String(255)))
        batch_op.alter_column('firm', 
                              new_column_name='initiator', 
                              type_=sa.String(255), 
                              existing_type=sa.Text())
        batch_op.alter_column('date_inq', 
                              new_column_name='deadline', 
                              type_=sa.Date(), 
                              existing_type=sa.Text())
        batch_op.alter_column('iquery_id', 
                              new_column_name='person_id')
        batch_op.drop_column('staff')
        batch_op.drop_column('period')

    # migrate registries table
    res = conn.execute(sa.text("select url, registry_id from registries"))
    results = res.fetchall()
    url_list = PathSchema().dump(results, many=True)
    for item in url_list:
        conn.execute(sa.text(
            "update persons set path = '{}' where id = {}"\
                .format(item['path'], item['registry_id']))
        )

    op.drop_table('registries')
    op.drop_table('candidates')
