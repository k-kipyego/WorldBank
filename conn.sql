SELECT 
    wb.id AS world_bank_id,
    wb.docdt AS document_date,
    wb.docty AS document_type,
    wb.display_title AS display_title,
    wb.pdfurl AS pdf_url,
    wb.listing_relative_url AS listing_url,
    wb.code AS project_id, -- Mapping code from world_bank to project_id
    wbn.id AS notice_id,
    wbn.notice_type,
    wbn.noticedate AS notice_date,
    wbn.notice_lang_name,
    wbn.notice_status,
    wbn.submission_deadline_date,
    wbn.submission_deadline_time,
    wbn.project_ctry_name,
    wbn.project_name,
    wbn.bid_reference_no,
    wbn.bid_description,
    wbn.procurement_group,
    wbn.procurement_method_code,
    wbn.procurement_method_name,
    wbn.contact_address,
    wbn.contact_ctry_name,
    wbn.contact_email,
    wbn.contact_name,
    wbn.contact_organization,
    wbn.contact_phone_no,
    wbn.submission_date
FROM world_bank wb
JOIN world_bank_notices wbn
ON wb.code = wbn.project_id;
