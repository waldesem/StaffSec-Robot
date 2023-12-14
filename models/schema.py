from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ..models.model import Category, Conclusion, Region, Status, Person, \
    Staff, Document, Address, Contact, Workplace, Affilation, Check, Robot, Inquiry


class RegionSchema(SQLAlchemyAutoSchema):
    """ Create model for location"""
    class Meta:
        model = Region 
        ordered = True


class CategorySchema(SQLAlchemyAutoSchema):
    """ Create model for category"""
    class Meta:
        model = Category 
        ordered = True


class StatusSchema(SQLAlchemyAutoSchema):
    """ Create model for status"""
    class Meta:
        model = Status 
        ordered = True


class PersonSchema(SQLAlchemyAutoSchema):
    """ Create model for person"""

    class Meta:
        model = Person
        ordered = True
        include_fk = True
        exclude = ('search_vector',)


class StaffSchema(SQLAlchemyAutoSchema):
    """ Create model for staff"""
    class Meta:
        model = Staff
        ordered = True


class DocumentSchema(SQLAlchemyAutoSchema):
    """ Create model for document"""
    class Meta:
        model = Document
        ordered = True
        exclude = ('search_vector',)


class AddressSchema(SQLAlchemyAutoSchema):
    """ Create model for address"""
    class Meta:
        model = Address
        ordered = True


class WorkplaceSchema(SQLAlchemyAutoSchema):
    """ Create model for workplace"""
    class Meta:
        model = Workplace
        ordered = True


class ContactSchema(SQLAlchemyAutoSchema):
    """ Create model for contact"""
    class Meta:
        model = Contact
        ordered = True


class AffilationSchema(SQLAlchemyAutoSchema):
    """ Create model for affilation"""
    class Meta:
        model = Affilation
        ordered = True


class CheckSchema(SQLAlchemyAutoSchema):
    """ Create model for check"""
    class Meta:
        model = Check
        ordered = True


class RobotSchema(SQLAlchemyAutoSchema):
    """ Create model for robot"""
    class Meta:
        model = Robot
        ordered = True


class ConclusionSchema(SQLAlchemyAutoSchema):
    """ Create model for conclusion"""
    class Meta:
        model = Conclusion 
        ordered = True


class InquirySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inquiry
        ordered = True
