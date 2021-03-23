
odoo.define('maintenance_buttons.section_and_note_backend', function (require) {
// The goal of this file is to contain JS hacks related to allowing
// section and note on sale order and invoice.

// [UPDATED] now also allows configuring products on sale order.

"use strict";
var FieldChar = require('web.basic_fields').FieldChar;
var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
var FieldMany2One = require('web.relational_fields').FieldMany2One;
var fieldRegistry = require('web.field_registry');
var ListFieldText = require('web.basic_fields').ListFieldText;
var ListRenderer = require('web.ListRenderer');



// This is a merge between a FieldText and a FieldChar.
// We want a FieldChar for section,
// and a FieldText for the rest (product and note).
var SectionAndNoteFieldMany2One = function (parent, name, record, options) {
    var isSection = record.data.display_type === 'line_section';
    var Constructor = FieldMany2One;
    return new Constructor(parent, name, record, options);
};

fieldRegistry.add('section_and_note_many2one', SectionAndNoteFieldMany2One);

return ListRenderer;
});
