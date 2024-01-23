# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from itertools import groupby
import json

import PyPDF2
import re
import io
from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt
from random import randint

import logging

_logger = logging.getLogger(__name__)





PROJECT_TASK_READABLE_FIELDS = {
    'id',
    'active',
    'description',
    'priority',
    'kanban_state_label',
    'project_id',
    'display_project_id',
    'color',
    'partner_is_company',
    'commercial_partner_id',
    'allow_subtasks',
    'subtask_count',
    'child_text',
    'is_closed',
    'email_from',
    'create_date',
    'write_date',
    'company_id',
    'displayed_image_id',
    'display_name',
    'portal_user_names',
    'legend_normal',
    'legend_blocked',
    'legend_done',
    'user_ids',
}

PROJECT_TASK_WRITABLE_FIELDS = {
    'name',
    'partner_id',
    'date_deadline',
    'tag_ids',
    'sequence',
    'stage_id',
    'kanban_state',
    'child_ids',
    'parent_id',
    'priority',
}



class TenderTracker(models.Model):
    _name = 'tender.initial'
    _description = 'Tender Initialization'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Tender Title', required=True, tracking=True)
    validity_period = fields.Integer(string='Validity Period (Days)', tracking=True)
    submission_deadline = fields.Datetime(string='Submission Deadline', tracking=True)
    opening_date = fields.Datetime(string='Tender Opening Date', tracking=True)
    document_fee = fields.Float(string='Document Fee')
    bid_bond_required = fields.Boolean(string='Bid Bond Required')
    eligibility_criteria = fields.Text(string='Eligibility Criteria')
    document = fields.Binary(string='Document', tracking=True)
    user_name = fields.Many2one('tender.users')
    email = fields.Char(related='user_name.email')

    extracted_text = fields.Text(string='Extracted Text')
    progress = fields.Integer()
    progress_percentage = fields.Float(compute='_compute_progress_percentage')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Starred")
    color = fields.Integer(string='Color Index')
    stage_id = fields.Many2one('tender.stage', string='Stage')
    tag_ids = fields.Many2one('tender.tags', string='Tags')
    kanban_state = fields.Selection([
        ('new', 'New'),
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('events', 'Events')], string='Status',
        copy=False, default='normal', required=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label')

    legend_new = fields.Char(related='stage_id.legend_new', string='Kanban New Explanation', readonly=True,
                                 related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Normal Explanation', readonly=True,
                             related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Done Explanation', readonly=True,
                              related_sudo=False)
    legend_events = fields.Char(related='stage_id.legend_events', string='Kanban Events Explanation', readonly=True,
                                related_sudo=False)







    @api.onchange('document')
    def _onchange_document(self):
        _logger.info("Onchange Document method triggered")
        try:
            if self.document:
                # Extract text from the document
                extracted_text = self.extract_text_from_pdf()
                _logger.info("Text has been extracted")
                self.update({'extracted_text': extracted_text})
                _logger.info("Extracted text has been saved into the 'extracted_text' variable")

                # Update tender information based on extracted text
                self.update_tender_info_from_text(extracted_text)
                _logger.info("Tender information updated using the extracted text")
        except Exception as e:
            _logger.error(f"Error during onchange_document: {e}")

    def extract_text_from_pdf(self):
        text = ''
        try:
            _logger.info("Inside the extract_text_from_pdf try clause")

            # Use PyPDF2 for text extraction
            #pdf_stream = io.BytesIO(self.document)
            _logger.info("BytesIO object created")
            _logger.info(type(self.document))
            pdf_reader = PyPDF2.PdfFileReader(self.document, strict=False)
            _logger.info("PyPDF2.PdfFileReader part executed")

            # Extract text from each page
            for page_num in range(pdf_reader.numPages):
                text += pdf_reader.getPage(page_num).extractText()
                _logger.info("For loop executed")


            _logger.info(f"Raw Extracted Text: {text}")
        except Exception as e:
            # Handle any extraction errors
            _logger.error(f"Error during text extraction: {e}")

        return text

    # def extract_text_from_pdf(self):
    #     text = ''
    #     try:
    #         _logger.info("Inside the extract_text_from_pdf try clause")
    #         # Create a BytesIO object for the PDF content
    #         pdf_stream = BytesIO(self.document)
    #         pdf_reader = PyPDF2.PdfFileReader(pdf_stream)
    #         pages = pdf_reader.getNumPages()
    #         no_of_pages = pdf_reader.getNumPages()
    #         _logger.info(f"The number of pages is {no_of_pages}")
    #
    #         for page_num in range(pages):
    #             text += pdf_reader.getPage(page_num).extractText()
    #
    #         for page_num in range(pdf_document.page_count):
    #             page = pdf_document[page_num]
    #             text += page.get_text()
    #
    #         _logger.info(f"Raw Extracted Text: {text}")
    #     # except PyPDF2.utils.PdfReadError as e:
    #     #     # Handle specific PyPDF2 exception for malformed PDF files
    #     #     _logger.warning(f"Error during text extraction (PdfReadError): {e}")
    #     except Exception as e:
    #         # Handle other extraction errors
    #         _logger.error(f"Error during text extraction: {e}")
    #     return text

    # def extract_text_from_pdf(self, document):
    #     text = ''
    #     try:
    #         _logger.info("Inside the extract_text_from_pdf try clause")
    #         # Create a BytesIO object for the PDF content
    #         # pdf_stream = BytesIO(self.document)
    #         # _logger.info("BytesIO object created")
    #         #
    #         # pdf_reader = PdfFileReader(pdf_stream, strict=False)
    #         # _logger.info("PdfFileReader object created")
    #
    #         pdf_reader = PdfFileReader(io.BytesIO(self.document), strict=False)
    #         _logger.info("PdfFileReader object created")
    #
    #         # Get document information
    #         number_of_pages = pdf_reader.getNumPages()
    #         _logger.info(f"Number of Pages: {number_of_pages}")
    #
    #         # Extract text from each page
    #         for page_num in range(number_of_pages):
    #             text += pdf_reader.getPage(page_num).extractText()
    #
    #         _logger.info(f"Raw Extracted Text: {text}")
    #     except Exception as e:
    #         # Handle any extraction errors
    #         _logger.error(f"Error during text extraction: {e}")
    #     return text



    def update_tender_info_from_text(self, text):
        # Extracting validity period
        validity_match = re.search(r'Validity Period: (\d+)', text)
        if validity_match:
            extracted_validity = int(validity_match.group(1))
            _logger.info(f"Extracted Validity Period: {extracted_validity}")
            self.update({'validity_period': extracted_validity})

        # other logic for other fields go here

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for tender in self:
            if tender.kanban_state == 'new':
                tender.kanban_state_label = tender.legend_new
            elif tender.kanban_state == 'normal':
                tender.kanban_state_label = tender.legend_normal
            elif tender.kanban_state == 'done':
                tender.kanban_state_label = tender.legend_done
            else:
                tender.kanban_state_label = tender.legend_events

    @api.depends('progress')
    def _compute_progress_percentage(self):
        for u in self:
            u.progress_percentage = u.progress / 100

    @api.depends('project_id')
    def _compute_stage_id(self):
        for task in self:
            if task.project_id:
                if task.project_id not in task.stage_id.project_ids:
                    task.stage_id = task.stage_find(task.project_id.id, [
                        ('fold', '=', False), ('is_closed', '=', False)])
            else:
                task.stage_id = False

    @property
    def SELF_READABLE_FIELDS(self):
        return PROJECT_TASK_READABLE_FIELDS | self.SELF_WRITABLE_FIELDS

    @property
    def SELF_WRITABLE_FIELDS(self):
        return PROJECT_TASK_WRITABLE_FIELDS

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100


# class TenderPreparation(models.Model):
#     _name = 'tender.preparation'
#     _description = 'Tender Preparation'
#     _inherit = 'tender.initial'
#
#     preparation_notes = fields.Binary(string='Preparation Notes')
#     technical_proposal = fields.Binary(string='Technical Proposal')
#     financial_proposal = fields.Binary(string='Financial Proposal')
#     preparation_completed = fields.Boolean(string='Preparation Completed', default=False)
#
#     # state = fields.Selection{[
#     #     ['new', 'New'],
#     #     ['review', 'Review'],
#     #     ['itt_compliance', 'ITT Compliance'],
#     #     ['submission', 'Submission'],
#     #     ['site_visits', 'Site Visits'],
#     # ], string='Status'}




class TenderTags(models.Model):
    """ Tags of tender's tasks """
    _name = "tender.tags"
    _description = "Tender Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class TenderUsers(models.Model):
    """ Tags of tender's users """
    _name = "tender.users"
    _description = "Tender Users"

    user_name = fields.Char('Name', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
