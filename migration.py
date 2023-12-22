from alembic import op
import sqlalchemy as sa

from models.classes import Categories, Conclusions, Regions, Statuses
from models.schema import DocumentSchema, PersonSchema, StaffSchema, PathSchema, \
    RegAddressSchema, LiveAddressSchema, PhoneContactSchema, EmailContactSchema, \
    CheckSchema, InquirySchema


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
        "SELECT id, staff, department FROM candidates"
    ))
    results = res.fetchall()
    schema = StaffSchema().dump(results, many=True)
    op.bulk_insert(staffs, schema)
    
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
        "SELECT id, series_passport, number_passport, date_given FROM candidates"
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
        "SELECT id, reg_address FROM candidates"
    ))
    res_live = conn.execute(sa.text(
        "SELECT id, live_address FROM candidates"
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
        "SELECT id, phone FROM candidates"
    ))
    res_mail = conn.execute(sa.text(
        "SELECT id, email FROM candidates"
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

    # migrate persons 
    persons = op.create_table(
        'persons',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('region_id', sa.Integer()),
        sa.ForeignKeyConstraint(('region_id',), ['regions.id'],),
        sa.Column('category_id', sa.Integer()),
        sa.ForeignKeyConstraint(('category_id',), ['categories.id'],),
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
        sa.Column('status_id', sa.Integer()),
        sa.ForeignKeyConstraint(('status_id',), ['statuses.id'],),
        sa.Column('create', sa.DateTime()),
        sa.Column('update', sa.DateTime())
    )
    res = conn.execute(sa.text(
        "SELECT id, full_name, last_name, birthday, birth_place, country, snils, inn, education FROM candidates"
    ))
    results = res.fetchall()
    op.bulk_insert(persons, PersonSchema().dump(results, many=True))

    checks = op.create_table(
        'new_checks',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('workplace', sa.Text()),
        sa.Column('document', sa.Text()),
        sa.Column('inn', sa.Text()),
        sa.Column('debt', sa.Text()),
        sa.Column('bankruptcy', sa.Text()),
        sa.Column('bki', sa.Text()),
        sa.Column('courts', sa.Text()),
        sa.Column('affilation', sa.Text()),
        sa.Column('terrorist', sa.Text()),
        sa.Column('mvd', sa.Text()),
        sa.Column('internet', sa.Text()),
        sa.Column('cronos', sa.Text()),
        sa.Column('cros', sa.Text()),
        sa.Column('addition', sa.Text()),
        sa.Column('pfo', sa.Boolean()),
        sa.Column('comments', sa.Text()),
        sa.Column('conclusion_id', sa.Integer()),
        sa.ForeignKeyConstraint(('conclusion_id',), ['conclusions.id'],),
        sa.Column('officer', sa.String(255)),
        sa.Column('deadline', sa.Date()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],),
    )
    res = conn.execute(sa.text(
        "SELECT check_work_place, check_passport, check_debt, check_bankruptcy, check_bki, check_affiliation, check_internet, check_cronos, check_cross, resume, officer, date_check, check_id FROM checks"
    ))
    results = res.fetchall()
    op.bulk_insert(checks, CheckSchema().dump(results, many=True))

    # migrate inquiries 
    inquiries = op.create_table(
        'inquiries',
        sa.Column('id', sa.Integer, primary_key=True, 
                  autoincrement=True, unique=True, nullable=False),
        sa.Column('info', sa.Text()),
        sa.Column('initiator', sa.String(255)),
        sa.Column('source', sa.String(255)),
        sa.Column('officer', sa.String(255)),
        sa.Column('deadline', sa.Date()),
        sa.Column('person_id', sa.Integer()),
        sa.ForeignKeyConstraint(('person_id',), ['persons.id'],)
    )
    res = conn.execute(sa.text(
        "SELECT id, info, firm, date_inq, iquery_id FROM iqueries"
    ))
    results = res.fetchall()
    op.bulk_insert(inquiries, InquirySchema().dump(results, many=True))

    # migrate registries
    res = conn.execute(sa.text("select url, registry_id from registries"))
    results = res.fetchall()
    url_list = PathSchema().dump(results, many=True)
    for item in url_list:
        conn.execute(sa.text(
            "update persons set path = '{}' where id = {}"\
                .format(item['path'], item['registry_id']))
        )
 
    # delete old tables
    op.drop_table('checks')
    op.drop_table('registries')
    op.drop_table('iqueries')
    op.drop_table('candidates')
    op.rename_table('new_checks', 'checks')