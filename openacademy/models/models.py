# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)


#

# class SaleOrderI(models.Model):
#     _inherit = "sale.order"
#     @api.multi
#     def action_invoice_create(self,*args,**kargs):
#         f = super(SaleOrderI,self).action_invoice_create
#         print 3333333333,'openacademy'#,f
#         rs=  f(*args,**kargs)
#         print 'end 3333333'
#         return  rs
# #     def hamx(self):
# #         res = super(SaleOrderI,self).hamx()
# #         print 'ham x in openacademy' 
class Testmodel(models.Model):
    _name = 'openacademy.testmodel'
    name = fields.Char(string="Title", required=True)
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course")
class Course(models.Model):
    _name = 'openacademy.course'
    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    si_so = fields.Integer(required = False)
    description2 = fields.Text()
    description3 = fields.Text()
    description4 = fields.Text()
    description5 = fields.Text()
    description6 = fields.Text()
    description7 = fields.Text()
    description8 = fields.Text()
    description9 = fields.Text()
    description10 = fields.Text()
    description11 = fields.Text()
    # description6 = fields.Text()
    responsible_id = fields.Many2one('res.users',
        ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many(
        'openacademy.session', 'course_id', string="session_ids")
    test_ids = fields.One2many(
        'openacademy.testmodel', 'course_id', string="test_ids")
    @api.model
    def create(self, vals):
        return super(Course, self).create(vals)
    
    @api.multi
    def write(self, vals):
        print '***write***********************',self._context
        return super(Course, self).write(vals)
    
    
    # attendee_ids = fields.Many2many('res.partner', string="Attendees_m2m_of_course")
    # session_m2m = fields.Many2many('openacademy.session', string="session_m2m")
# class Course2(models.Model):
#     _name = 'openacademy.course'
#     name = fields.Char(string="Title", required=True)
#     description = fields.Text()
#     si_so = fields.Integer(required = False)
#     description2 = fields.Text(string = "des2",required = True)
#     description3 = fields.Text()
#     description4 = fields.Text()
#     description5 = fields.Text()
#     description82 = fields.Text()
#     description51 = fields.Text()
#     description92 = fields.Text()
#     description102 = fields.Text()
#     # description112 = fields.Text()
#     description113 = fields.Text()
#     responsible_id = fields.Many2one('res.users',
#         ondelete='set null', string="Responsible", index=True)

#     session_ids = fields.One2many(
#         'openacademy.session', 'course_id', string="Sessions_one2many")

class Session(models.Model):
    _name = 'openacademy.session'
    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats",)
    instructor_id = fields.Many2one('res.partner',string="Instructor")#domain=[('instructor', '=', True)]
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course")
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    place_owner_ids = fields.Many2many('res.partner', string="place owner")
    giai_thich_session = fields.Text(default='anh nho em')
    taken_seats = fields.Float(string="Taken seats",)# compute='_taken_seats'
    active = fields.Boolean(default=True)
    end_date = fields.Date(string="End Date", store=True,
        compute='_get_end_date', inverse='_set_end_date')
    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)
    color = fields.Integer()
    state = fields.Selection([
        
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('done', "Done")
    ],default='draft')
    # trangthai = fields.Selection([
        
    #     ('draft', "Draft"),
    #     ('confirmed', "Confirmed"),
    #     ('done', "Done")
    # ],default = 'done')
    @api.multi
    def write(self, vals):
        print '***write***********************ss',self._context
        return super(Session, self).write(vals)
    
    @api.model
    def create(self, vals):
        print '***create***********************ss',self._context
        return super(Session, self).create(vals)
    @api.multi
    def action_draft(self):
        print "self.env['ir.config_parameter']********",self.env['ir.config_parameter']
        print self.env['ir.config_parameter'].get_param('oss_wholesale_protocol')
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        print '********context**********',self._context
        self.state = 'confirmed'

    @api.multi
    def action_done(self):
        self.state = 'done'
    #@api.depends('seats', 'attendee_ids')
    @api.onchange('name')
    def test_onchange_name(self):
        print '..................reload lai la onchange ngay................'

    @api.onchange('seats', 'attendee_ids')
    def _taken_seats(self):
        print '**********nhay vao on change tinh ghe,in context luon', self._context
        print '****r.seats',self.seats
        print '****'
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats
    @api.constrains('instructor_id', )
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")

    # @api.onchange('seats', 'attendee_ids')
    # def _verify_valid_seats(self):
    #     if self.seats < 0:
    #         return {
    #             'warning': {
    #                 'title': "Incorrect 'seats' value",
    #                 'message': "The number of available seats may not be negative",
    #             },
    #         }
    #     if self.seats < len(self.attendee_ids):
    #         return {
    #             'warning': {
    #                 'title': "Too many attendees",
    #                 'message': "Increase seats or remove excess attendees",
    #             },
    #         }

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]
    
    @api.model
    def default_get(self, fields):
        res = super(Session, self).default_get(fields)
        print 'taken_seats defautlget',res.get('taken_seats')
        print 'd4'*50
        print 'default get',res,'type(res)',type(res)
        print 'res.get("giai_thich_session")',res.get("giai_thich_session")
        print 'fields',fields
        res['giai_thich_session'] = 'alooooooooooooo'
        return res

    # add ngay 15/03
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        print '*****************test***********'
        # print '***all ss',self.env['openacademy.session'].search([]).mapped('course_id.name')
        # print '***all ss',self.env['openacademy.session'].search([]).filtered(lambda r: 'a' in r.name )[0][0][0].name
        print '**quan torng ***',self.attendee_ids.ids

        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue
            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            start = fields.Datetime.from_string(r.start_date)
            print 'start******date',start,type(start)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1


    @api.depends('duration')
    def _get_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def _set_hours(self):
        for r in self:
            r.duration = r.hours / 24

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)
    
class Partner(models.Model):
    _inherit = 'res.partner'

    # Add a new column to the res.partner model, by default partners are not
    # instructors
    instructor = fields.Boolean("Instructor", default=False)
    session_ids = fields.Many2many('openacademy.session',
        string="Attended Sessions", readonly=True)



class SaleOrder(models.Model):
    _inherit = "sale.order"
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=False, copy=False, index=True, track_visibility='onchange', default='draft')