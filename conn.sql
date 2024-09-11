-- Create the new table to store the combined results
CREATE TABLE worldbankCombined AS
SELECT 
    wbn.id AS notice_id,
    wbn.notice_type,
    wbn.noticedate,
    wbn.notice_lang_name,
    wbn.notice_status,
    wbn.submission_deadline_date,
    wbn.submission_deadline_time,
    wbn.project_ctry_name,
    wbn.project_id,
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
    wbn.submission_date,
    wb.docty,
    wb.docdt,
    wb.display_title,
    wb.pdfurl,
    wb.listing_relative_url
FROM 
    world_bank_notices AS wbn
JOIN 
    world_bank AS wb 
ON 
    wbn.project_id = wb.code
WHERE 
    wbn.submission_deadline_date >= '2024-01-01'  -- Limit tenders to 2024 onwards
    AND wbn.submission_deadline_date <= '2024-12-31';  -- Filter only for tenders in 2024
