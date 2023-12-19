from alembic import op
import sqlalchemy as sa


def upgrade_db():
    op.rename_table('candidates', 'persons')
    op.rename_table('iqueries', 'inquiries')

    # create new tables
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('category', sa.String(255))
    )
    op.create_table(
        'statuses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('status', sa.String(255))
    )
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('region', sa.String(255))
    )
    op.create_table(
        'conclusions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('conclusion', sa.String(255))
    )
    op.create_table(
        'staffs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('position', sa.Text()),
        sa.Column('department', sa.Text()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('series', sa.String(255)),
        sa.Column('number', sa.String(255)),
        sa.Column('agency', sa.Text()),
        sa.Column('issue', sa.Date()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('region', sa.String(255)),
        sa.Column('address', sa.Text()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False),
        sa.Column('view', sa.String(255)),
        sa.Column('contact', sa.String(255)),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    op.create_table(
        'workplaces',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False),
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
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False),
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
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False),
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
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False),
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
        batch_op.alter_column('full_name', new_column_name='fullname', type_=sa.String(255), existing_type=sa.Text())

        batch_op.alter_column('last_name', new_column_name='previous', type_=sa.String(255), existing_type=sa.Text())

        batch_op.alter_column('birthday',type_=sa.Date(), existing_type=sa.Text())

        batch_op.alter_column('birth_place', new_column_name='birthplace', type_=sa.String(255), existing_type=sa.Text())

        batch_op.alter_column('country',type_=sa.String(255), existing_type=sa.Text())

        batch_op.alter_column('snils',type_=sa.String(12), existing_type=sa.Text())

        batch_op.alter_column('inn',type_=sa.String(11), existing_type=sa.Text())

    op.add_column('persons', sa.Column('category_id', sa.Integer()), 
    sa.ForeignKey('categories.id'))
    op.add_column('persons', sa.Column('region_id', sa.Integer()), 
    sa.ForeignKey('regions.id'))
    op.add_column('persons', sa.Column('status_id', sa.Integer()), 
    sa.ForeignKey('statuses.id'))
    op.add_column('persons', sa.Column('ext_country', sa.String(255)))
    op.add_column('persons', sa.Column('marital', sa.String(255)))
    op.add_column('persons', sa.Column('path', sa.Text()))
    op.add_column('persons', sa.Column('create', sa.Date()))
    op.add_column('persons', sa.Column('update', sa.Date()))

    # migrate check table
    with op.batch_alter_table('checks') as batch_op:
        batch_op.alter_column('check_work_place', new_column_name='workplace')

        batch_op.alter_column('check_passport', new_column_name='document')

        batch_op.alter_column('check_debt', new_column_name='debt')

        batch_op.alter_column('check_bankruptcy', new_column_name='bankruptcy')

        batch_op.alter_column('check_bki', new_column_name='bki')

        batch_op.alter_column('check_affiliation', new_column_name='affiliation')

        batch_op.alter_column('check_internet', new_column_name='internet')

        batch_op.alter_column('check_work_place', new_column_name='workplace')

        batch_op.alter_column('check_cronos', new_column_name='cronos')

        batch_op.alter_column('check_cross', new_column_name='cros')

        batch_op.alter_column('officer', type_=sa.String(255), existing_type=sa.Text())

        batch_op.alter_column('date_check', new_column_name='deadline', type_=sa.Date(), existing_type=sa.Text())

        batch_op.alter_column('check_id', new_column_name='person_id')

    op.add_column('checks', sa.Column('comments', sa.Text()))
    op.add_column('checks', sa.Column('pfo', sa.Boolean()))
    op.add_column('checks', sa.Column('addition', sa.Text()))
    op.add_column('checks', sa.Integer()), 
    sa.ForeignKey('categories.id')
    
    op.drop_column('checks', 'resume')

    # migrate inquiries table
    op.drop_column('inquiries', 'staff')
    op.drop_column('inquiries', 'period')
    op.add_column('inquiries', sa.Column('source', sa.String(255)))
    op.add_column('inquiries', sa.Column('officer', sa.String(255)))
    with op.batch_alter_table('iqueries') as batch_op:
        batch_op.alter_column('firm', new_column_name='initiator', type_=sa.String(255), existing_type=sa.Text())

        batch_op.alter_column('date_inq', new_column_name='deadline', type_=sa.Date(), existing_type=sa.Text())

        batch_op.alter_column('iquery_id', new_column_name='person_id')

    # migrate registries table
    op.drop_table('registries')
