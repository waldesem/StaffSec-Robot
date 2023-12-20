from alembic import op
import sqlalchemy as sa

from models.classes import Categories, Conclusions, Regions, Statuses


def upgrade_db():

    op.rename_table('candidates', 'persons')
    op.rename_table('iqueries', 'inquiries')
    
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

    persons = sa.Table('persons', metadata)

    for person in persons:
        op.bulk_insert(staffs, [{
            'position': person.staff, 
            'department': person.department, 
            'person_id': person.id
            }])

    op.create_table(
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
    documents = sa.Table('documents', op.get_bind())
    for person in persons:
        op.bulk_insert(documents, [{
            'series': person.series_passport, 
            'number': person.number_passport, 
            'issue': person.date_given, 
            'person_id': person.id
            }])
    
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('region', sa.String(255)),
        sa.Column('address', sa.Text()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    addresses = sa.Table('addresses', op.get_bind())
    for person in persons:
        op.bulk_insert(addresses, [
            {'view': 'Адрес регистрации', 
             'address': person.reg_address, 
             'person_id': person.id},
            {'view': 'Адрес проживания', 
             'address': person.live_address, 
             'person_id': person.id}
        ])
    
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('contact', sa.String(255)),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    contacts = sa.Table('contacts', op.get_bind())
    for person in persons:
        op.bulk_insert(contacts, [
            {'view': 'Номер телефона', 
             'contact': person.phone, 
             'person_id': person.id},
            {'view': 'Электронная почта', 
             'contact': person.email, 
             'person_id': person.id}
        ])
    
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
        sa.Column('comment', sa.String(255)),
        sa.Column('data', sa.String(255)),
    )

    # migrate persons table
    with op.batch_alter_table('persons') as batch_op:
        batch_op.alter_column('full_name', 
                              new_column_name='fullname', 
                              type_=sa.String(255), 
                              existing_type=sa.Text())

        batch_op.alter_column('last_name', 
                              new_column_name='previous', 
                              type_=sa.String(255), 
                              existing_type=sa.Text())

        batch_op.alter_column('birthday',type_=sa.Date(), 
                              existing_type=sa.Text())

        batch_op.alter_column('birth_place', 
                              new_column_name='birthplace', 
                              type_=sa.String(255), 
                              existing_type=sa.Text())

        batch_op.alter_column('country',
                              type_=sa.String(255), 
                              existing_type=sa.Text())

        batch_op.alter_column('snils',
                              type_=sa.String(12), 
                              existing_type=sa.Text())

        batch_op.alter_column('inn',
                              type_=sa.String(11), 
                              existing_type=sa.Text())

        batch_op.add_column(sa.Column('category_id', sa.Integer(), 
                                      sa.ForeignKey('categories.id', 
                                                    name='fk_persons_category_id')))
        batch_op.add_column('persons', 
                            sa.Column('region_id', sa.Integer(), 
                                      sa.ForeignKey('regions.id',
                                                    name='fk_persons_region_id')))
        batch_op.add_column('persons', 
                            sa.Column('status_id', sa.Integer(), 
                                      sa.ForeignKey('statuses.id',
                                                    name='fk_persons_status_id')))
        batch_op.add_column('persons', 
                            sa.Column('ext_country', sa.String(255)))
        batch_op.add_column('persons', 
                            sa.Column('marital', sa.String(255)))
        batch_op.add_column('persons', 
                            sa.Column('path', sa.Text()))
        batch_op.add_column('persons', 
                            sa.Column('create', sa.Date()))
        batch_op.add_column('persons', 
                            sa.Column('update', sa.Date()))

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
        batch_op.add_column(sa.Integer(), sa.ForeignKey('categories.id'))
    
    op.drop_column('checks', 'resume')

    # migrate inquiries table
    op.drop_column('inquiries', 'staff')
    op.drop_column('inquiries', 'period')
    op.add_column('inquiries', sa.Column('source', sa.String(255)))
    with op.batch_alter_table('iqueries') as batch_op:
        batch_op.add_column('inquiries', 
                            sa.Column('officer', sa.String(255)))
        batch_op.alter_column('firm', 
                              new_column_name='initiator', 
                              type_=sa.String(255), 
                              existing_type=sa.Text())
        batch_op.alter_column('date_inq', 
                              new_column_name='deadline', 
                              type_=sa.Date(), 
                              existing_type=sa.Text())
        batch_op.alter_column('iquery_id', new_column_name='person_id')

    # migrate registries table
    registries = sa.Table('registries', op.get_bind())
    for reg in registries:
        person =persons.select().where(persons.c.id == reg.c.registry_id)
        persons.update().where(persons.c.id == reg.c.registry_id).values(
            path=reg.c.url,
        )
    op.drop_table('registries')