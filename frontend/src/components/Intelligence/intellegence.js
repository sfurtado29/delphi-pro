// Intelligence.js — Enterprise Redesign
import React, { useState, useRef, useEffect, useCallback, useMemo } from "react";
import "./intellegence.css";

const API_BASE   = "http://127.0.0.1:8000";
const API_HOST = (process.env.REACT_APP_API_DOMAIN || process.env.REACT_APP_API_BASE || API_BASE).replace(/\/$/, "");
const SESSION_ID = `user_${Math.random().toString(36).slice(2, 9)}`;

// Sample leads payload for local/dev testing (injected when using ICP)
const SAMPLE_LEADS = [
  {
    "LEAD_ID": 43258,
    "FIRST_NAME": "Don",
    "LAST_NAME": "McLean",
    "COMPANY_NAME": "Postlethwaite & Netterville",
    "JOB_TITLE": "Director",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Management",
    "INDUSTRY": "Accounting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 278805,
    "FIRST_NAME": "Ellen",
    "LAST_NAME": "Clay",
    "COMPANY_NAME": "Veristor",
    "JOB_TITLE": "Director Sales Operations",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 278844,
    "FIRST_NAME": "Robyn",
    "LAST_NAME": "Beier",
    "COMPANY_NAME": "MicroTech",
    "JOB_TITLE": "Sales Director",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 278925,
    "FIRST_NAME": "Robbie",
    "LAST_NAME": "Luethold",
    "COMPANY_NAME": "Thrive",
    "JOB_TITLE": "Regional Vice President of Sales",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Information Technology and Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 285934,
    "FIRST_NAME": "Aaron",
    "LAST_NAME": "Scutt",
    "COMPANY_NAME": "Technology Integration Group",
    "JOB_TITLE": "Vice President of Field Sales",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Information Technology and Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 285941,
    "FIRST_NAME": "Bill",
    "LAST_NAME": "Morton",
    "COMPANY_NAME": "Technology Integration Group",
    "JOB_TITLE": "Vice President / Eastern Field Sales",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Information Technology and Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 285966,
    "FIRST_NAME": "Brett",
    "LAST_NAME": "Apold",
    "COMPANY_NAME": "ARCOA Group",
    "JOB_TITLE": "Vice President of Sales",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Information Technology and Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 286020,
    "FIRST_NAME": "David",
    "LAST_NAME": "Chapman",
    "COMPANY_NAME": "Standley Systems",
    "JOB_TITLE": "Director of Sales",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Information Technology and Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 221154,
    "FIRST_NAME": "Rob",
    "LAST_NAME": "Thomas",
    "COMPANY_NAME": "Waterlogic",
    "JOB_TITLE": "Vice President Sales Operations",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Food & Beverages",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 227425,
    "FIRST_NAME": "Tina",
    "LAST_NAME": "Christiansen",
    "COMPANY_NAME": "ConsultNet",
    "JOB_TITLE": "Sr. Director of Sales",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Staffing & Recruiting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 351602,
    "FIRST_NAME": "Bill",
    "LAST_NAME": "Eastman",
    "COMPANY_NAME": "Oakwood Systems Group",
    "JOB_TITLE": "Senior Director - Enterprise Sales",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Information Technology & Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 48466,
    "FIRST_NAME": "Martin",
    "LAST_NAME": "Aguilar",
    "COMPANY_NAME": "Canopy",
    "JOB_TITLE": "Director of Sales & Marketing at Canopy by Hilton Jersey City Arts District",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "Hospitality",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 278154,
    "FIRST_NAME": "Michael",
    "LAST_NAME": "Ellison",
    "COMPANY_NAME": "BlueAlly",
    "JOB_TITLE": "VP of Sales",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 278197,
    "FIRST_NAME": "Darryl",
    "LAST_NAME": "Drenon",
    "COMPANY_NAME": "Centre Technologies",
    "JOB_TITLE": "Vice President, Sales",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 278210,
    "FIRST_NAME": "Colby",
    "LAST_NAME": "Van Vooren",
    "COMPANY_NAME": "Ednetics",
    "JOB_TITLE": "Vice President of Sales",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 278245,
    "FIRST_NAME": "Hank",
    "LAST_NAME": "Hathaway",
    "COMPANY_NAME": "Executech",
    "JOB_TITLE": "Vice President of Sales & Marketing",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 278259,
    "FIRST_NAME": "Ben",
    "LAST_NAME": "Berghall",
    "COMPANY_NAME": "ImageNet Consulting, LLC",
    "JOB_TITLE": "VP of Sales and Marketing",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 278386,
    "FIRST_NAME": "Max",
    "LAST_NAME": "Holl",
    "COMPANY_NAME": "Technologent",
    "JOB_TITLE": "Sr Director, Sales Operations",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Sales",
    "INDUSTRY": "IT Services and IT Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 254429,
    "FIRST_NAME": "Julie",
    "LAST_NAME": "Comiskey",
    "COMPANY_NAME": "LogicSource, Inc.",
    "JOB_TITLE": "Vice President Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Facilities",
    "INDUSTRY": "Management Consulting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 108257,
    "FIRST_NAME": "Susan",
    "LAST_NAME": "Mciver",
    "COMPANY_NAME": "ABI Document Support Services",
    "JOB_TITLE": "Director of Finance",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Facilities",
    "INDUSTRY": "Legal Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 57194,
    "FIRST_NAME": "Kenan",
    "LAST_NAME": "Ozcan",
    "COMPANY_NAME": "High Caliber Line",
    "JOB_TITLE": "Vice President of Finance Corporate Controller",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Facilities",
    "INDUSTRY": "Marketing and Advertising",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 57217,
    "FIRST_NAME": "Joe",
    "LAST_NAME": "Sayers",
    "COMPANY_NAME": "Chick-Fil-A College Football Hall Of Fame",
    "JOB_TITLE": "Finance and Data Analytics Manager",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Facilities",
    "INDUSTRY": "Sports",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 57712,
    "FIRST_NAME": "Matthew",
    "LAST_NAME": "Cunningham",
    "COMPANY_NAME": "Best Formulations Inc.",
    "JOB_TITLE": "Vice President Of Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Facilities",
    "INDUSTRY": "Pharmaceuticals",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 160281,
    "FIRST_NAME": "Ryan",
    "LAST_NAME": "Mundie",
    "COMPANY_NAME": "Student Transportation Inc",
    "JOB_TITLE": "Manager of Finance",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "TransportationTruckingRailroad",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 160298,
    "FIRST_NAME": "Michael",
    "LAST_NAME": "Levy",
    "COMPANY_NAME": "Student Transportation Inc",
    "JOB_TITLE": "Director of Finance",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "TransportationTruckingRailroad",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 160482,
    "FIRST_NAME": "Rob",
    "LAST_NAME": "Brown",
    "COMPANY_NAME": "Clēnera",
    "JOB_TITLE": "Finance Manager",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Renewables & Environment",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 54484,
    "FIRST_NAME": "Jojo",
    "LAST_NAME": "Dizon",
    "COMPANY_NAME": "Authentic Brands Group",
    "JOB_TITLE": "Executive Vice President of Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Marketing and Advertising",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 55692,
    "FIRST_NAME": "Barbara",
    "LAST_NAME": "Nicotera",
    "COMPANY_NAME": "Kettle",
    "JOB_TITLE": "Director of Finance",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Marketing and Advertising",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 55733,
    "FIRST_NAME": "Paxton",
    "LAST_NAME": "Morris",
    "COMPANY_NAME": "The Physicians Spine & Rehabilitation Specialists",
    "JOB_TITLE": "Director of Finance",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Medical Practice",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 56941,
    "FIRST_NAME": "Allen",
    "LAST_NAME": "Blanton",
    "COMPANY_NAME": "StructureTec Group",
    "JOB_TITLE": "Senior Financial Reporting Manager",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Facilities Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 57234,
    "FIRST_NAME": "Lara",
    "LAST_NAME": "McKissick",
    "COMPANY_NAME": "KTGY ARCHITECTURE + PLANNING",
    "JOB_TITLE": "Director of Accounting",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Architecture & Planning",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 57626,
    "FIRST_NAME": "Ryan",
    "LAST_NAME": "Gardner",
    "COMPANY_NAME": "Lawrence & Schiller",
    "JOB_TITLE": "Vice President of Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Marketing And Advertising",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 61091,
    "FIRST_NAME": "Brett",
    "LAST_NAME": "Scott",
    "COMPANY_NAME": "All Medical Personnel",
    "JOB_TITLE": "Director of Accounting and Finance",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Staffing and Recruiting",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 61100,
    "FIRST_NAME": "Bret",
    "LAST_NAME": "Adams",
    "COMPANY_NAME": "IMS Consulting & Expert Services",
    "JOB_TITLE": "VP of Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Legal Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 61106,
    "FIRST_NAME": "Christina Mattioli",
    "LAST_NAME": "Mattioli",
    "COMPANY_NAME": "Magna Legal Services",
    "JOB_TITLE": "Accounting Manager",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Legal Services",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 61205,
    "FIRST_NAME": "Matthew",
    "LAST_NAME": "Lewis",
    "COMPANY_NAME": "Proed Communications",
    "JOB_TITLE": "Associate Client Finance Director",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Marketing and Advertising",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 61346,
    "FIRST_NAME": "Tim",
    "LAST_NAME": "Hill",
    "COMPANY_NAME": "Nippon Dynawave Packaging Co.",
    "JOB_TITLE": "Vice President of Finance and Treasurer",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Packaging and Containers",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 61533,
    "FIRST_NAME": "Maira",
    "LAST_NAME": "dos Santos",
    "COMPANY_NAME": "Kencor, LLC Elevator Systems",
    "JOB_TITLE": "Accounting Manager",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Construction",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 61581,
    "FIRST_NAME": "Vanessa",
    "LAST_NAME": "Voigt",
    "COMPANY_NAME": "TF Cornerstone",
    "JOB_TITLE": "Executive Assistant to the Chairman, Executive VP of Finance & Director of Planning",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Real Estate",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 41818,
    "FIRST_NAME": "Kyla",
    "LAST_NAME": "Kuntz",
    "COMPANY_NAME": "Anonymous Content",
    "JOB_TITLE": "Vice President of Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Entertainment",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 41824,
    "FIRST_NAME": "Mikael",
    "LAST_NAME": "Karlsson",
    "COMPANY_NAME": "Anonymous Content",
    "JOB_TITLE": "Senior Vice President Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Entertainment",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 41851,
    "FIRST_NAME": "Eric",
    "LAST_NAME": "Frayer",
    "COMPANY_NAME": "Dick Clark Productions",
    "JOB_TITLE": "SVP Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Newspapers",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 41871,
    "FIRST_NAME": "Emily",
    "LAST_NAME": "Arnold",
    "COMPANY_NAME": "Maslansky + Partners",
    "JOB_TITLE": "Finance Manager",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Marketing & Advertising",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 41896,
    "FIRST_NAME": "Alan",
    "LAST_NAME": "Bendich",
    "COMPANY_NAME": "The Forward",
    "JOB_TITLE": "VP, Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Newspapers",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 41916,
    "FIRST_NAME": "Edward",
    "LAST_NAME": "Shimmin",
    "COMPANY_NAME": "Proximo Spirits",
    "JOB_TITLE": "Senior Vice President Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Wine and Spirits",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 41951,
    "FIRST_NAME": "Frayer",
    "LAST_NAME": "EricFray",
    "COMPANY_NAME": "DICK CLARK PRODUCTION",
    "JOB_TITLE": "SVP Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Entertainment",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 42120,
    "FIRST_NAME": "Johanna",
    "LAST_NAME": "Valverde",
    "COMPANY_NAME": "Proximo Spirits",
    "JOB_TITLE": "Accounting Director",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Wine and Spirits",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 43271,
    "FIRST_NAME": "Allison",
    "LAST_NAME": "Brake",
    "COMPANY_NAME": "Carnegie Communications",
    "JOB_TITLE": "VP Finance",
    "JOB_LEVEL_DESC": "VP",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Marketing and Advertising",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  },
  {
    "LEAD_ID": 43452,
    "FIRST_NAME": "Beth",
    "LAST_NAME": "Pendergast",
    "COMPANY_NAME": "Hord Coplan Macht",
    "JOB_TITLE": "Finance Manager",
    "JOB_LEVEL_DESC": "Manager",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Architecture & Planning",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "250-499"
  },
  {
    "LEAD_ID": 43465,
    "FIRST_NAME": "Paul",
    "LAST_NAME": "Crosbie",
    "COMPANY_NAME": "Harris Farms, Inc.",
    "JOB_TITLE": "Director of Finance",
    "JOB_LEVEL_DESC": "Director",
    "JOBFUNCTION_DESC": "Finance",
    "INDUSTRY": "Farming",
    "LOCATION_DESC": "United States",
    "EMPLOYEE_SIZE_DESC": "100-249"
  }
];

// ── Field definitions ────────────────────────────────────────────────────────

const PRODUCT_FIELD_LABELS = {
  product_description:  "Product",
  product_name:         "Product Name",
  product_usps:         "USPs",
  product_pricing_tier: "Positioning",
  campaign_budget:      "Budget",
  ideal_buyer:          "Ideal Buyer",
  target_market_type:   "Market Type",
  buyer_stage:          "Buyer Stage",
};

const PRODUCT_FIELD_ORDER = [
  "product_description", "product_name", "product_usps",
  "product_pricing_tier", "campaign_budget", "ideal_buyer",
  "target_market_type", "buyer_stage",
];

const TARGETING_FIELD_LABELS = {
  geography:     "Geography",
  industry:      "Industry",
  job_function:  "Job Function",
  job_level:     "Seniority",
  employee_size: "Company Size",
  revenue_range: "Lead Revenue",
};

const TARGETING_FIELD_ORDER = [
  "geography", "industry", "job_function",
  "job_level", "employee_size", "revenue_range",
];

const SUGGESTION_LABELS = {
  geography:     "Target Geographies",
  industry:      "Industries",
  job_function:  "Job Functions",
  job_level:     "Seniority Levels",
  employee_size: "Company Sizes",
  revenue_range: "Lead Revenue Ranges",
};

const ALL_FIELDS = [...PRODUCT_FIELD_ORDER, ...TARGETING_FIELD_ORDER];

// ── Utility: parse lead text strings ────────────────────────────────────────
function parseLeadText(text) {
  if (typeof text !== "string") return null;
  const row = {};
  const companyMatch = text.match(/Lead works at ([^.]+)\./);
  if (companyMatch) row["Company"] = companyMatch[1].trim();
  const pairs = [
    ["Industry",      /Industry:\s*([^.]+)\./],
    ["Job Title",     /Job title:\s*([^.]+)\./],
    ["Job Function",  /Job function:\s*([^.]+)\./],
    ["Seniority",     /Seniority:\s*([^.]+?)(?:\.|$)/],
    ["Employee Size", /Employee[_ ](?:size|count)?:\s*([^.]+)\./i],
    ["Revenue",       /Revenue[_ ]range:\s*([^.]+)\./i],
    ["Geography",     /Geography:\s*([^.]+)\./i],
    ["Domain",        /(?:domain|sector):\s*([^.]+)\./i],
  ];
  for (const [key, rx] of pairs) {
    const m = text.match(rx);
    if (m) row[key] = m[1].trim();
  }
  return Object.keys(row).length > 0 ? row : null;
}

function normalizeRow(row) {
  if (typeof row === "string") return parseLeadText(row) || { Profile: row };
  if (row && typeof row === "object") {
    const map = {
      company_name:         "Company",
      company:              "Company",
      campaign_information: "Company",
      name:                 "Company",
      client_name:          "Company",
      COMPANY_NAME:         "Company",
      COMPANY:              "Company",

      FIRST_NAME:           "First Name",
      first_name:           "First Name",
      LAST_NAME:            "Last Name",
      last_name:            "Last Name",
      contact_name:         "Contact",
      contact:              "Contact",
      CONTACT_NAME:         "Contact",
      CONTACT:              "Contact",

      job_title:            "Job Title",
      title:                "Job Title",
      job_title_desc:       "Job Title",
      JOB_TITLE:            "Job Title",
      JOB_TITLE_DESC:       "Job Title",
      TITLE:                "Job Title",

      job_level:            "Seniority",
      job_level_desc:       "Seniority",
      seniority:            "Seniority",
      JOB_LEVEL:            "Seniority",
      JOB_LEVEL_DESC:       "Seniority",
      SENIORITY:            "Seniority",

      industry:             "Industry",
      target_industry:      "Industry",
      INDUSTRY:             "Industry",
      TARGET_INDUSTRY:      "Industry",

      job_function:         "Job Function",
      jobfunction_desc:     "Job Function",
      JOBFUNCTION_DESC:     "Job Function",
      JOB_FUNCTION:         "Job Function",
      JOB_FUNCTION_DESC:    "Job Function",

      hq_location:          "Geography",
      country:              "Geography",
      target_geography:     "Geography",
      location_desc:        "Geography",
      HQ_LOCATION:          "Geography",
      COUNTRY:              "Geography",
      TARGET_GEOGRAPHY:     "Geography",
      LOCATION_DESC:        "Geography",

      employees:            "Employee Size",
      target_employee_size: "Employee Size",
      employee_size_desc:   "Employee Size",
      EMPLOYEES:            "Employee Size",
      TARGET_EMPLOYEE_SIZE: "Employee Size",
      EMPLOYEE_SIZE_DESC:   "Employee Size",
      EMPLOYEE_SIZE:        "Employee Size",

      revenue_size:         "Revenue",
      target_revenue_size:  "Revenue",
      REVENUE_SIZE:         "Revenue",
      TARGET_REVENUE_SIZE:  "Revenue",
      REVENUE_RANGE:        "Revenue",

      email:                "Email",
      email_address:        "Email",
      EMAIL:                "Email",
      EMAIL_ADDRESS:        "Email",

      phone:                "Phone",
      PHONE:                "Phone",

      icp_fit:              "ICP Fit",
      icp_score:            "ICP Fit",
      ICP_FIT:              "ICP Fit",
      ICP_SCORE:            "ICP Fit",
      propensity_score:     "Propensity",
      propensity:           "Propensity",
      PROPENSITY_SCORE:     "Propensity",
      PROPENSITY:           "Propensity",

      LEAD_ID:              "__LEAD_ID__",
      lead_id:              "__LEAD_ID__",
    };

    const out = {};
    for (const [k, v] of Object.entries(row)) {
      const target = map[k] || map[String(k).toUpperCase()] || null;
      if (target && target !== "__LEAD_ID__") {
        if (target === "First Name") {
          out["Contact"] = [row["FIRST_NAME"] || row["first_name"] || "", row["LAST_NAME"] || row["last_name"] || ""].filter(Boolean).join(" ") || (v ?? "—");
          continue;
        }
        if (target === "Last Name") continue;
        if (!(target in out)) out[target] = v ?? "—";
      }
    }
    for (const [k, v] of Object.entries(row)) {
      const target = map[k] || map[String(k).toUpperCase()] || null;
      if (!target) {
        const label = k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        if (!(label in out)) out[label] = v ?? "—";
      }
    }
    return out;
  }
  return { Value: String(row) };
}

const PRIORITY_COLS = [
  "Contact", "Company", "Job Title", "Seniority",
  "Industry", "Job Function", "Employee Size", "Revenue", "Geography",
];

function sortColumns(cols) {
  const priority = PRIORITY_COLS.filter(c => cols.includes(c));
  const rest = cols.filter(c => !PRIORITY_COLS.includes(c));
  return [...priority, ...rest];
}

// ── Seniority badge ──────────────────────────────────────────────────────────
const SENIORITY_COLORS = {
  "c level":       { bg: "#fef3c7", text: "#92400e", border: "#fcd34d" },
  "c-level":       { bg: "#fef3c7", text: "#92400e", border: "#fcd34d" },
  "chief":         { bg: "#fef3c7", text: "#92400e", border: "#fcd34d" },
  "ceo":           { bg: "#fef3c7", text: "#92400e", border: "#fcd34d" },
  "cto":           { bg: "#fef3c7", text: "#92400e", border: "#fcd34d" },
  "cfo":           { bg: "#fef3c7", text: "#92400e", border: "#fcd34d" },
  "vp":            { bg: "#ede9fe", text: "#4c1d95", border: "#c4b5fd" },
  "vice president":{ bg: "#ede9fe", text: "#4c1d95", border: "#c4b5fd" },
  "director":      { bg: "#dbeafe", text: "#1e40af", border: "#93c5fd" },
  "manager":       { bg: "#dcfce7", text: "#14532d", border: "#86efac" },
  "senior":        { bg: "#f0fdf4", text: "#166534", border: "#bbf7d0" },
};

function SeniorityBadge({ value }) {
  if (!value) return <span className="lt-cell-dash">—</span>;
  const key = value.toLowerCase();
  const style = Object.entries(SENIORITY_COLORS).find(([k]) => key.includes(k))?.[1];
  if (!style) return <span className="lt-cell-text">{value}</span>;
  return (
    <span className="lt-seniority-badge"
      style={{ background: style.bg, color: style.text, border: `1px solid ${style.border}` }}>
      {value}
    </span>
  );
}

const INDUSTRY_ICONS = {
  software: "💻", technology: "💻", computers: "💻",
  healthcare: "🏥", health: "🏥",
  finance: "🏦", financial: "🏦", banking: "🏦", fintech: "🏦",
  manufacturing: "🏭",
  retail: "🛍️",
  education: "🎓",
  "real estate": "🏢",
  energy: "⚡",
  media: "📺", entertainment: "📺",
  telecommunications: "📡",
  agriculture: "🌾",
  accounting: "📊",
  consulting: "💼",
  staffing: "👥",
  recruiting: "👥",
  "it services": "🖥️",
  "information technology": "🖥️",
  legal: "⚖️",
  pharmaceuticals: "💊",
  construction: "🏗️",
  "food": "🍽️",
  hospitality: "🏨",
  sports: "🏆",
  marketing: "📣",
  "architecture": "📐",
  renewables: "♻️",
};

function IndustryCell({ value }) {
  if (!value) return <span className="lt-cell-dash">—</span>;
  const icon = Object.entries(INDUSTRY_ICONS).find(([k]) => value.toLowerCase().includes(k))?.[1] || "🏢";
  return (
    <span className="lt-industry-cell">
      <span>{icon}</span>
      {value}
    </span>
  );
}

// ── Leads Table ──────────────────────────────────────────────────────────────
function LeadsTable({ rows }) {
  const [page, setPage]               = useState(0);
  const [sortCol, setSortCol]         = useState(null);
  const [sortDir, setSortDir]         = useState("asc");
  const [search, setSearch]           = useState("");
  const [expandedRow, setExpandedRow] = useState(null);
  const PAGE_SIZE = 15;

  const normalized = useMemo(() =>
    !rows?.length ? [] : rows.map(normalizeRow).filter(Boolean), [rows]);

  const columns = useMemo(() => {
    if (!normalized.length) return [];
    const allKeys = new Set();
    normalized.forEach(r => Object.keys(r).forEach(k => allKeys.add(k)));
    return sortColumns([...allKeys]);
  }, [normalized]);

  const filtered = useMemo(() => {
    if (!search.trim()) return normalized;
    const q = search.toLowerCase();
    return normalized.filter(row =>
      Object.values(row).some(v => String(v).toLowerCase().includes(q))
    );
  }, [normalized, search]);

  const sorted = useMemo(() => {
    if (!sortCol) return filtered;
    return [...filtered].sort((a, b) => {
      const av = String(a[sortCol] ?? "");
      const bv = String(b[sortCol] ?? "");
      return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    });
  }, [filtered, sortCol, sortDir]);

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
  const pageRows   = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const handleSort = col => {
    if (sortCol === col) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortCol(col); setSortDir("asc"); }
    setPage(0);
  };

  const pageWindow = () => {
    const start = Math.max(0, Math.min(page - 2, totalPages - 5));
    return Array.from({ length: Math.min(5, totalPages) }, (_, i) => start + i);
  };

  if (!rows?.length) {
    return (
      <div className="lt-empty">
        <div className="lt-empty-icon">🔍</div>
        <p>No matching leads found for this criteria.</p>
      </div>
    );
  }

  return (
    <div className="lt-wrapper">
      <div className="lt-toolbar">
        <div className="lt-count">
          <span className="lt-count-num">{sorted.length}</span>
          <span className="lt-count-label">leads found</span>
        </div>
        <div className="lt-search-wrap">
          <svg className="lt-search-icon" width="13" height="13" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
            <path d="M16.5 16.5L21 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <input
            className="lt-search-input"
            placeholder="Filter results..."
          />
        </div>
      </div>

      <div className="lt-scroll">
        <table className="lt-table">
          <thead>
            <tr>
              <th className="lt-th lt-th-num">#</th>
              {columns.map(col => (
                <th key={col} className={`lt-th`} onClick={() => handleSort(col)}>
                  <div className="lt-th-inner">{col}{sortCol===col && <span className="lt-sort-icon">{sortDir==='asc'?' ▲':' ▼'}</span>}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, idx) => (
              <tr key={row.__id || idx} className={`lt-row ${expandedRow === idx ? 'lt-row-expanded' : ''}`} onClick={() => setExpandedRow(expandedRow === idx ? null : idx)}>
                <td className="lt-td lt-td-num">{page * PAGE_SIZE + idx + 1}</td>
                {columns.map(col => (
                  <td key={col} className="lt-td">{row[col] ?? '—'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="lt-pagination">
          <span className="lt-page-info">Page {page + 1} of {totalPages} · {sorted.length} results</span>
          <div className="lt-page-btns">
            <button className="lt-page-btn" disabled={page === 0} onClick={() => setPage(0)}>«</button>
            <button className="lt-page-btn" disabled={page === 0} onClick={() => setPage(p => p - 1)}>‹</button>
            {pageWindow().map(p => (
              <button key={p}
                className={`lt-page-btn ${p === page ? "lt-page-btn-active" : ""}`}
                onClick={() => setPage(p)}
              >{p + 1}</button>
            ))}
            <button className="lt-page-btn" disabled={page === totalPages - 1} onClick={() => setPage(p => p + 1)}>›</button>
            <button className="lt-page-btn" disabled={page === totalPages - 1} onClick={() => setPage(totalPages - 1)}>»</button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── History Item with 3-dot menu ───────────────────────────────────────────
function HistoryItem({ chat, isActive, onLoad, onStar, onDelete }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <div
      className={`history-item ${isActive ? "active" : ""}`}
      onClick={() => { onLoad(chat); setOpen(false); }}
    >
      <span className="history-item-title">{chat.title}</span>
      <div className="hist-menu-wrap" ref={menuRef}>
        <button
          className="hist-dots-btn"
          title="Options"
          onClick={e => { e.stopPropagation(); setOpen(v => !v); }}
        >⋯</button>
        {open && (
          <div className="hist-dropdown">
            <button className="hist-dd-item" onClick={e => { e.stopPropagation(); onStar(chat.id); setOpen(false); }}>
              {chat.starred ? "★ Unstar" : "☆ Star"}
            </button>
            <button className="hist-dd-item danger" onClick={e => { e.stopPropagation(); onDelete(chat.id); setOpen(false); }}>
              🗑 Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function SidebarPanel({ title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="sidebar-panel">
      <button className="sidebar-panel-header" onClick={() => setOpen(v => !v)}>
        <span className="sidebar-panel-title">{title}</span>
        <span className={`sidebar-panel-chevron ${open ? "open" : ""}`}>›</span>
      </button>
      {open && <div className="sidebar-panel-body">{children}</div>}
    </div>
  );
}

function ContextPill({ label, value }) {
  return (
    <div className="context-pill">
      <span className="pill-label">{label}</span>
      <span className="pill-value" title={value}>{value}</span>
    </div>
  );
}

function TypingDots() {
  return (
    <div className="typing-indicator">
      <span /><span /><span />
    </div>
  );
}

function SuggestionGroup({ field, items, onSelect, disabled = false }) {
  return (
    <div className="suggestion-group">
      <div className="suggestion-group-label">
        <span>{SUGGESTION_LABELS[field] || field}</span>
      </div>
      <div className="suggestion-chips">
        {Array.isArray(items) && (() => {
          const uniq = Array.from(new Set(items.map(it => (typeof it === 'string' ? it.trim() : it))));
          return uniq.map(item => (
            <button key={item} className={`chip ${disabled ? 'disabled' : ''}`} onClick={() => !disabled && onSelect(item)} disabled={disabled}>
              {item}
            </button>
          ));
        })()}
      </div>
    </div>
  );
}

function SuggestionCard({ field, items, onContinue, disabled = false, contextValues = null }) {
  const [selected, setSelected] = React.useState([]);
  const handleChipClick = (it) => {
    if (disabled) return;
    setSelected(prev => {
      try {
        const copy = Array.isArray(prev) ? [...prev] : [];
        const idx = copy.indexOf(it);
        if (idx >= 0) copy.splice(idx, 1);
        else copy.push(it);
        return copy;
      } catch (e) { return prev; }
    });
  };

  const isSelected = (it) => {
    const sArr = Array.isArray(selected) ? selected : [];
    const cArr = Array.isArray(contextValues) ? contextValues : (contextValues ? [contextValues] : []);
    return sArr.includes(it) || cArr.includes(it);
  };

  return (
    <div className="suggestion-group" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div className="suggestion-group-label"><span>{SUGGESTION_LABELS[field] || field}</span></div>
      <div className="suggestion-chips">
        {Array.isArray(items) && (() => {
          const uniq = Array.from(new Set(items.map(it => (typeof it === 'string' ? it.trim() : it))));
          return uniq.map(it => (
            <button key={it} className={`chip ${isSelected(it) ? 'selected' : ''}`} onClick={() => handleChipClick(it)}>{it}</button>
          ));
        })()}
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
        <button className="continue-btn" onClick={() => onContinue(selected)} disabled={!Array.isArray(selected) || selected.length === 0}>
          Continue →
        </button>
      </div>
    </div>
  );
}

function ProgressBar({ filled, total }) {
  const pct = total > 0 ? Math.round((filled / total) * 100) : 0;
  return (
    <div className="progress-bar-wrap">
      <div className="progress-bar-track">
        <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="progress-label">{pct}%</span>
    </div>
  );
}

function PhaseBadge({ phase }) {
  if (!phase || phase === "complete") return null;
  const isProduct = phase === "product";
  const label = isProduct ? "Product & Campaign" : "Audience Targeting";
  const color = isProduct ? "var(--violet)" : "var(--accent)";
  const bg    = isProduct ? "var(--violet-soft)" : "var(--accent-soft)";
  return (
    <div className="phase-badge" style={{ background: bg, color, borderColor: color }}>
      <span className="phase-dot" style={{ background: color }} />
      {label}
    </div>
  );
}

// ── Helper: extract leads array from any response shape ─────────────────────
function extractLeads(data) {
  if (!data) return null;

  // If the response *is* an array of leads
  if (Array.isArray(data) && data.length > 0) return data;

  // Common property names (case-sensitive)
  const candidate = data.leads || data.data || data.results || data.rows || data.records;
  if (Array.isArray(candidate) && candidate.length > 0) return candidate;

  // Be more permissive: if any top-level property is an array of objects,
  // treat that as the leads payload (handles variations like 'LEADS' or
  // vendor-specific keys).
  try {
    for (const k of Object.keys(data || {})) {
      const v = data[k];
      if (Array.isArray(v) && v.length > 0 && v.every(it => typeof it === "object")) return v;
    }
  } catch (e) {
    // ignore and fall through
  }

  return null;
}

// Normalize suggestions object from backend: ensure arrays are deduped and trimmed
function normalizeSuggestions(sugs) {
  if (!sugs) return {};
  // If an array is provided, return a deduped array
  if (Array.isArray(sugs)) {
    const seen = new Set();
    return sugs
      .map(it => (typeof it === 'string' ? it.trim() : it))
      .filter(it => {
        if (typeof it === 'string') {
          if (!it) return false;
          if (seen.has(it)) return false;
          seen.add(it);
          return true;
        }
        return true;
      });
  }
  if (typeof sugs !== 'object') return {};
  const out = {};
  try {
    for (const k of Object.keys(sugs)) {
      const v = sugs[k];
      if (Array.isArray(v)) {
        const seen = new Set();
        out[k] = v
          .map(it => (typeof it === 'string' ? it.trim() : it))
          .filter(it => {
            if (typeof it === 'string') {
              if (!it) return false;
              if (seen.has(it)) return false;
              seen.add(it);
              return true;
            }
            return true;
          });
      } else {
        out[k] = v;
      }
    }
  } catch (e) { return {}; }
  return out;
}

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════

export default function Intellegence() {
  const [messages,      setMessages]      = useState([]);
  const [chatSelectedProducts, setChatSelectedProducts] = useState([]);
  const [chatProductInput, setChatProductInput] = useState("");
  const [singleCardSelections, setSingleCardSelections] = useState({});
  const [input,         setInput]         = useState("");
  const [loading,       setLoading]       = useState(false);
  const [context,       setContext]       = useState({});
  const [suggestions,   setSuggestions]   = useState({});
  const [isFetching,    setIsFetching]    = useState(false);
  const [phase,         setPhase]         = useState("product");
  const [chatHistory,   setChatHistory]   = useState([]);
  const [activeChatId,  setActiveChatId]  = useState(null);
  const [chatTitle,     setChatTitle]     = useState("");
  const [sidebarOpen,   setSidebarOpen]   = useState(true);
  const [darkMode,      setDarkMode]      = useState(() => {
    return localStorage.getItem("delphi-theme") === "dark";
  });

  const bottomRef      = useRef(null);
  const textareaRef    = useRef(null);
  const sessionRef     = useRef(SESSION_ID);

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.setAttribute("data-theme", "dark");
      localStorage.setItem("delphi-theme", "dark");
    } else {
      root.removeAttribute("data-theme");
      localStorage.setItem("delphi-theme", "light");
    }
  }, [darkMode]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, suggestions, loading]);

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 140) + "px";
  }, [input]);

  const user = useMemo(() => {
    try { return JSON.parse(localStorage.getItem("user") || "{}"); } catch { return {}; }
  }, []);

  const userInitials = useMemo(() => {
    const name = user.full_name || user.email || "D";
    return name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
  }, [user]);

  const currentChatTitle = useMemo(() => {
    if (activeChatId) {
      const active = chatHistory.find(c => c.id === activeChatId);
      return active?.title || "Saved Search";
    }
    if (chatTitle) return chatTitle;
    const userMessage = messages.find(m => m.role === "user")?.text || "";
    return userMessage ? userMessage.slice(0, 42) : "New Search";
  }, [activeChatId, chatHistory, messages, chatTitle]);

  const toggleStarChat = (chatId) => {
    setChatHistory(prev => prev.map(chat =>
      chat.id === chatId ? { ...chat, starred: !chat.starred } : chat
    ));
  };

  const deleteChat = (chatId) => {
    setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
    if (activeChatId === chatId) {
      setActiveChatId(null);
      setMessages([]);
      setContext({});
      setSuggestions({});
      setPhase("product");
      setChatTitle("");
    }
  };

  const pushMessage = useCallback(msg => {
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), ...msg }]);
  }, []);

  const initiateICP = useCallback(async () => {
    const userId = user.user_id || user.id || null;
    pushMessage({ role: 'user', text: 'Create Ideal Company Profile' });
    setLoading(true);
    try {
      const res = await fetch(`${API_HOST}/campaign/profile`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      });
      const jd = await res.json().catch(() => ({}));
      if (jd && jd.success) {
        pushMessage({ role: 'bot', text: 'We found these products from your profile:' });
        const items = Array.isArray(jd.all_products) ? jd.all_products.map(p => (typeof p === 'string' ? { label: p } : p)) : [];
        pushMessage({ role: 'bot', type: 'products', products: items });
        // Do not auto-select scraped products; let the user choose which to add.
      } else {
        pushMessage({ role: 'bot', text: jd.message || 'No scraped products found.' });
      }
    } catch (e) {
      pushMessage({ role: 'bot', text: 'Failed to load scraped products.' });
    } finally {
      setLoading(false);
    }
  }, [pushMessage, user]);

  const fetchLeadsAfterIcp = useCallback(async (sessionId, userId, attempt = 0) => {
    const MAX = 10;
    const DELAYS = [1000, 2000, 3000, 5000, 5000, 5000, 5000, 5000, 5000, 5000];

    if (attempt >= MAX) {
      setIsFetching(false);
      pushMessage({ role: 'bot', text: 'Lead generation is taking longer than expected. Please try again in a moment.' });
      return;
    }

    await new Promise(r => setTimeout(r, DELAYS[attempt]));

    try {
      const res = await fetch(`${API_HOST}/campaign/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, user_id: userId, message: 'continue' }),
      });
      const data = await res.json();
      console.log(`[FETCH LEADS attempt ${attempt + 1}]`, data.status, data.stage, data);

      if (data.context) setContext(data.context);
      if (data.phase)   setPhase(data.phase);
      if (data.stage)   setPhase(data.stage);

      const leads = extractLeads(data);

      if (leads && leads.length > 0) {
        setIsFetching(false);
        if (data.response) pushMessage({ role: 'bot', text: data.response });
        pushMessage({ role: 'bot', table: leads, leads_count: data.leads_count || data.count || leads.length });
        setSuggestions({});
      } else if (data.status === 'completed' || data.status === 'complete') {
        setIsFetching(false);
        if (data.response) pushMessage({ role: 'bot', text: data.response });
        if (data.summary)  pushMessage({ role: 'bot', text: data.summary });
      } else {
        fetchLeadsAfterIcp(sessionId, userId, attempt + 1);
      }
    } catch (err) {
      console.error('[FETCH LEADS error]', err);
      fetchLeadsAfterIcp(sessionId, userId, attempt + 1);
    }
  }, [pushMessage]);

  const sendMessage = useCallback(async (text) => {
    const raw = (typeof text !== 'undefined' && text !== null) ? text : input;
    let finalText = '';
    if (typeof raw === 'string') finalText = raw.trim();
    else if (Array.isArray(raw)) finalText = raw.join(', ').trim();
    else if (typeof raw === 'number') finalText = String(raw).trim();
    else finalText = '';

    if (!finalText || loading) return;

    // We'll handle simple client-side lead operations after showing the user's message

    const userId = user.user_id || user.id || null;

    if (messages.length === 0 && !activeChatId) {
      const newId = Date.now();
      const newChat = { id: newId, title: finalText.slice(0, 42), messages: [], context: {} };
      setChatHistory(prev => [newChat, ...prev]);
      setActiveChatId(newId);
    }

    pushMessage({ role: "user", text: finalText });
    setInput("");

    

    setLoading(true);
    setSuggestions({});

    try {
      const res = await fetch(`${API_HOST}/campaign/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionRef.current, user_id: userId, message: finalText }),
      });

      const data = await res.json();
      console.log("[API Response]", data);

      if (data.context) setContext(data.context);
      if (data.phase)   setPhase(data.phase);
      if (data.stage)   setPhase(data.stage);

      if (data.icp_table || data.icp_rows) {
        pushMessage({
          role: 'bot', type: 'icp',
          narrative: data.response || '',
          icp_table: data.icp_table || [],
          icp_rows: data.icp_rows || [],
          quick_replies: data.quick_replies || [],
        });
        setSuggestions({});
      } else if (data.response) {
        pushMessage({ role: "bot", text: data.response, editApplied: data.edit_applied || null });
      }

      setSuggestions(normalizeSuggestions(data.suggestions ?? {}));

      const leads = extractLeads(data);
      const stillPending = new Set(['fetching', 'processing', 'pending', 'running']);
      if (leads && leads.length > 0) {
        setIsFetching(false);
        const count = data.leads_count || data.count || leads.length;
        pushMessage({ role: "bot", table: leads, leads_count: count });
        setSuggestions({});
      } else if (stillPending.has(data.status) || stillPending.has(data.stage)) {
        setIsFetching(true);
      } else {
        setIsFetching(false);
      }

      if ((data.status === "completed" || data.status === "complete") && !leads) {
        if (data.summary) pushMessage({ role: "bot", text: data.summary });
        setSuggestions({});
      }

      if (data.status === 'icp_accepted' && (!leads || leads.length === 0)) {
        setIsFetching(true);
        fetchLeadsAfterIcp(sessionRef.current, userId);
      }

    } catch (err) {
      console.error(err);
      pushMessage({ role: "bot", text: "Something went wrong connecting to the server. Please try again." });
    } finally {
      setLoading(false);
    }
  }, [input, loading, pushMessage, messages, activeChatId, user]);

  // Toggle selection for single-card suggestion groups (e.g., geography)
  const toggleSingleSelection = (field, item) => {
    setSingleCardSelections(prev => {
      const copy = { ...(prev || {}) };
      const arr = Array.isArray(copy[field]) ? [...copy[field]] : [];
      const idx = arr.indexOf(item);
      if (idx >= 0) arr.splice(idx, 1); else arr.push(item);
      copy[field] = arr;
      return copy;
    });
  };

  const handleSingleContinue = (field) => {
    const sel = Array.isArray(singleCardSelections[field]) ? singleCardSelections[field] : [];
    if (!sel.length) return;
    setContext(prev => {
      try {
        const prevVal = prev?.[field];
        if (Array.isArray(prevVal)) return { ...prev, [field]: Array.from(new Set([...prevVal, ...sel])) };
        return { ...prev, [field]: sel.length === 1 ? sel[0] : sel };
      } catch (e) { return prev; }
    });
    // Preserve visible suggestion chips immediately — calling sendMessage
    // normally clears `suggestions` at the start. Capture current suggestions
    // and restore them so chips remain present while the request runs.
    const currentSugs = suggestions;
    sendMessage(sel).catch(() => {});
    setSuggestions(currentSugs);
    // keep suggestions visible; don't clear them
  };

  

    // Handle ICP quick-reply actions. In development, intercept the
    // "Use this profile for my campaign" action and inject SAMPLE_LEADS
    // directly so the `LeadsTable` renders immediately without waiting
    // for backend lead-generation.
    const handleIcpAction = async (qr) => {
      const text = (qr || "").toString();
      // When user accepts the ICP, immediately show the two Delphi responses
      // so the UI doesn't feel like it's waiting. Then continue the normal flow.
      if (text.toLowerCase().includes('use this profile')) {
        setIsFetching(true);
        pushMessage({ role: 'bot', text: "Using your selected ICP, we're analyzing potential prospects and calculating lead propensity scores to surface the most relevant opportunities." });
        pushMessage({ role: 'bot', text: "We've identified 50 high-potential prospects that closely match your Ideal Customer Profile." });
      }

      if (process.env.NODE_ENV !== 'production' && text.toLowerCase().includes('use this profile')) {
        // dev-only: quickly inject sample leads for testing (no extra message)
        setIsFetching(false);
        pushMessage({ role: 'bot', table: SAMPLE_LEADS, leads_count: SAMPLE_LEADS.length });
        setSuggestions({});
        return;
      }

      // Default behaviour: send the ICP acceptance to backend
      await sendMessage(text);
    };

  const handleKeyDown = e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewChat = async () => {
    if (messages.length > 0 && activeChatId) {
      setChatHistory(prev => prev.map(c =>
        c.id === activeChatId ? { ...c, messages, context } : c
      ));
    }
    try {
      await fetch(`${API_HOST}/context/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionRef.current }),
      });
    } catch {}
    setMessages([]);
    setInput("");
    setSuggestions({});
    setContext({});
    setPhase("product");
    setActiveChatId(null);
  };

  const loadChat = chat => {
    setMessages(chat.messages);
    setContext(chat.context || {});
    setSuggestions({});
    setActiveChatId(chat.id);
  };

  const filledProductFields   = PRODUCT_FIELD_ORDER.filter(f => context[f]);
  const filledTargetingFields = TARGETING_FIELD_ORDER.filter(f => context[f]);
  const totalFilled           = filledProductFields.length + filledTargetingFields.length;
  const hasAnyContext         = totalFilled > 0;

  return (
    <div className={`app-shell ${sidebarOpen ? "sidebar-open" : ""}`}>

      {/* ══ SIDEBAR ══════════════════════════════════════════════ */}
      <aside className="sidebar">
        <button className="new-chat-btn" onClick={startNewChat}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
            <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
          </svg>
          New Search
        </button>

        <PhaseBadge phase={phase} />

        <div className="sidebar-context-scroll">
          {filledProductFields.length > 0 && (
            <SidebarPanel title="Product & Campaign" defaultOpen>
              {filledProductFields.map(f => (
                <ContextPill key={f} label={PRODUCT_FIELD_LABELS[f]} value={context[f]} />
              ))}
            </SidebarPanel>
          )}

          {filledTargetingFields.length > 0 && (
            <SidebarPanel title="Audience Context" defaultOpen>
              {filledTargetingFields.map(f => (
                <ContextPill key={f} label={TARGETING_FIELD_LABELS[f]} value={context[f]} />
              ))}
            </SidebarPanel>
          )}

          {hasAnyContext && (
            <div className="overall-progress">
              <span className="overall-label">Profile complete</span>
              <ProgressBar filled={totalFilled} total={ALL_FIELDS.length} />
            </div>
          )}
        </div>

        <div className="sidebar-campaign-placeholder" />

        <div className="sidebar-bottom">
          {chatHistory.some(c => c.starred) && (
            <div className="sidebar-history">
              <div className="history-section-label">⭐ Starred</div>
              <div className="history-list">
                {chatHistory.filter(c => c.starred).map(chat => (
                  <HistoryItem key={chat.id} chat={chat} isActive={activeChatId === chat.id}
                    onLoad={loadChat} onStar={toggleStarChat} onDelete={deleteChat} />
                ))}
              </div>
            </div>
          )}

          <div className="sidebar-history">
            <div className="history-section-label">History</div>
            <div className="history-list">
              {chatHistory.filter(c => !c.starred).map(chat => (
                <HistoryItem key={chat.id} chat={chat} isActive={activeChatId === chat.id}
                  onLoad={loadChat} onStar={toggleStarChat} onDelete={deleteChat} />
              ))}
              {chatHistory.length === 0 && messages.length === 0 && (
                <p className="history-empty">Your searches will appear here</p>
              )}
            </div>
          </div>
        </div>
      </aside>

      {!sidebarOpen && (
        <button className="sidebar-reopen" onClick={() => setSidebarOpen(true)} title="Open sidebar">›</button>
      )}

      {/* ══ MAIN PANEL ═══════════════════════════════════════════ */}
      <main className="main-panel">
        <div className="chat-topbar">
          <span className="chat-title-text">{currentChatTitle || "New Search"}</span>
        </div>

        {messages.length === 0 && (
          <div className="delphi-hero">
            <div className="delphi-logo">Welcome{user.full_name ? ` ${user.full_name.split(" ")[0].toLowerCase()}` : ""}</div>
            <h1 className="delphi-hero-title">How can I help you?</h1>
            <p className="delphi-hero-subtitle">Ask anything about leads, companies, competitors, market intelligence, or industry insights.</p>

            <div className="hero-cards">
              <div className="hero-cards-row">
                <button className="hero-card" onClick={() => initiateICP()}><span>Create Ideal Company Profile</span><span className="card-arrow">→</span></button>
                <button className="hero-card" onClick={() => sendMessage("Uncover Personas")}><span>Uncover Personas</span><span className="card-arrow">→</span></button>
                <button className="hero-card" onClick={() => sendMessage("Identify buyer groups")}><span>Identify buyer groups</span><span className="card-arrow">→</span></button>
                <button className="hero-card" onClick={() => sendMessage("Geo-based personalization")}><span>Geo-based personalization</span><span className="card-arrow">→</span></button>
              </div>
              <div className="hero-cards-row">
                <button className="hero-card" onClick={() => sendMessage("Create TAL")}><span>Create TAL</span><span className="card-arrow">→</span></button>
                <button className="hero-card" onClick={() => sendMessage("Filter existing TAL to prioritize accounts")}><span>Filter existing TAL to prioritize accounts</span><span className="card-arrow">→</span></button>
                <button className="hero-card" onClick={() => sendMessage("Uncover industries")}><span>Uncover industries</span><span className="card-arrow">→</span></button>
              </div>
            </div>
          </div>
        )}

        <div className={`messages-area ${messages.length === 0 ? "no-scroll" : ""}`}>
          {messages.map(msg => (
            // ── KEY CHANGE: React.Fragment wraps each message so the table
            //    can render as a sibling OUTSIDE message-content constraints
            <React.Fragment key={msg.id}>
              <div className={`message-row ${msg.role}`}>
                {msg.role === "bot" && (
                  <div className="bot-avatar" title="Delphi AI">D</div>
                )}
                {msg.role === "user" && (
                  <div className="user-avatar" title={user.full_name || user.email || 'You'}>{userInitials}</div>
                )}
                <div className="message-content">
                  {msg.text && <div className="bubble">{msg.text}</div>}

                  {/* ── Products picker ── */}
                  {msg.type === 'products' && Array.isArray(msg.products) && (
                    <div className="product-card">
                      <div className="product-card-chips">
                        {msg.products.map((p, idx) => {
                          const label = p.label || '';
                          const selected = chatSelectedProducts.includes(label);
                          return (
                            <button key={idx}
                              className={`chip ${selected ? 'selected' : ''}`}
                              onClick={() => {
                                setChatSelectedProducts(prev => prev.includes(label) ? prev.filter(x => x !== label) : [...prev, label]);
                              }}
                            >{label}</button>
                          );
                        })}
                      </div>
                      <div className="product-card-actions">
                        <input className="product-input" value={chatProductInput} onChange={e => setChatProductInput(e.target.value)}
                          placeholder="Or type a different product..." />
                        <button className="mp-manage-btn" onClick={() => {
                          const v = (chatProductInput||'').trim(); if(!v) return; setChatProductInput('');
                          setChatSelectedProducts(prev => prev.includes(v) ? prev : [v, ...prev]);
                        }}>+ Add</button>
                        <button className="mp-manage-btn primary" onClick={async () => {
                          if (!chatSelectedProducts.length) { alert('Select at least one product'); return; }
                          const uid = user.user_id || user.id || null;
                          if (!uid) { alert('No user id'); return; }
                          try {
                            const res = await fetch(`${API_HOST}/profile/${uid}/products`, {
                              method: 'POST', headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ products: chatSelectedProducts, company_type: '' }),
                            });
                            let jd = {};
                            try { jd = await res.json(); } catch(e) { jd = { raw: await res.text() }; }
                            if (res.ok && jd && jd.success) {
                              pushMessage({ role: 'bot', text: 'Saved selected products as Ideal Company Profile.' });
                              const selectedLabel = chatSelectedProducts[0] || chatSelectedProducts.join(', ');
                              try {
                                const startRes = await fetch(`${API_HOST}/campaign/start`, {
                                  method: 'POST', headers: { 'Content-Type': 'application/json' },
                                  body: JSON.stringify({ session_id: sessionRef.current, brand: selectedLabel }),
                                });
                                const startJson = await startRes.json().catch(() => ({}));
                                if (startJson) {
                                  if (startJson.response) pushMessage({ role: 'bot', text: startJson.response });
                                  if (startJson.suggestions) setSuggestions(normalizeSuggestions(startJson.suggestions || {}));
                                  if (startJson.stage) setPhase(startJson.stage);
                                }
                              } catch (e) { console.warn('Failed to start campaign pipeline', e); }
                              setChatSelectedProducts([]);
                            } else {
                              alert('Could not save to server — check console for details.');
                            }
                          } catch (err) { alert('Network error saving selection.'); }
                        }}>Use Selected</button>
                      </div>
                    </div>
                  )}

                  {/* ── ICP card ── */}
                  {msg.type === 'icp' && (
                    <div style={{ marginTop: 12 }}>
                      <div className="icp-card">
                        <div className="icp-heading">ICP Generated</div>
                        <div className="icp-body" dangerouslySetInnerHTML={{ __html: msg.narrative || '' }} />
                        <div className="icp-actions">
                          {(msg.quick_replies && msg.quick_replies.length > 0
                            ? msg.quick_replies
                            : ["Use this profile for my campaign", "Define my own criteria"]
                          ).map((qr, i) => (
                            <button key={i} className={`icp-btn ${i===0? 'primary':''}`} onClick={() => handleIcpAction(qr)}>
                              {qr}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {msg.editApplied && (
                    <div className="edit-badge">
                      ✓ Updated: {msg.editApplied.field?.replace(/_/g, " ")} → {msg.editApplied.value}
                    </div>
                  )}
                </div>
              </div>

              {/* ── Leads table renders OUTSIDE message-content so it gets full width ── */}
              {msg.table !== undefined && (
                <div className="leads-table-row">
                  <LeadsTable rows={msg.table} />
                </div>
              )}
            </React.Fragment>
          ))}

          {(loading || isFetching) && (
            <div className="message-row bot">
              <div className="bot-avatar">D</div>
              <div className="message-content">
                <div className="bubble"><TypingDots /></div>
              </div>
            </div>
          )}

          {(!loading && !isFetching) && (Array.isArray(suggestions) ? (
            <div className="suggestions-area">
              <SuggestionGroup field={'suggestions'} items={suggestions} onSelect={sendMessage} />
            </div>
          ) : (suggestions && Object.keys(suggestions).length > 0) ? (
            <div className="suggestions-area">
                  {(() => {
                    // If geography suggestions exist, render them inside a single card
                    const entries = Object.entries(suggestions || {});
                    const seen = new Set();
                    const targetingFields = TARGETING_FIELD_ORDER.filter(f => Array.isArray(suggestions?.[f]) && suggestions[f].length > 0);
                    const nodes = [];

                    if (targetingFields.length > 0) {
                      nodes.push(
                        <div key="single-targeting" className="single-suggestion-card">
                          {targetingFields.map(field => (
                            <div key={field} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                              <div className="suggestion-group-label"><span>{SUGGESTION_LABELS[field] || field}</span></div>
                              <div className="suggestion-chips">
                                {suggestions[field].map(it => {
                                  const label = (typeof it === 'string') ? it.trim() : it;
                                  const selected = Array.isArray(singleCardSelections[field]) && singleCardSelections[field].includes(label);
                                  return (
                                    <button key={field + '::' + label} className={`chip ${selected ? 'selected' : ''}`} onClick={() => toggleSingleSelection(field, label)}>{label}</button>
                                  );
                                })}
                              </div>
                            </div>
                          ))}

                          <div style={{ display: 'flex', gap: 8 }}>
                            {targetingFields.map(f => (
                              <button key={`c-${f}`} className="continue-btn" onClick={() => handleSingleContinue(f)}
                                disabled={!Array.isArray(singleCardSelections[f]) || singleCardSelections[f].length === 0}>
                                Continue →
                              </button>
                            ))}
                          </div>
                        </div>
                      );

                      // mark seen items so they don't duplicate below
                      for (const f of targetingFields) {
                        suggestions[f].forEach(it => seen.add(typeof it === 'string' ? it.trim() : it));
                      }
                    }

                    for (const [field, items] of entries) {
                      if (targetingFields.includes(field)) continue; // already rendered in single card
                      if (!Array.isArray(items)) {
                        nodes.push(
                          <SuggestionCard key={field} field={field} items={items} disabled={isFetching}
                            contextValues={context?.[field]}
                            onContinue={(sel) => {
                              if (!sel) return;
                              const selectionArray = Array.isArray(sel) ? sel : [sel];
                              setContext(prev => {
                                try {
                                  const prevVal = prev?.[field];
                                  if (Array.isArray(prevVal)) {
                                    return { ...prev, [field]: Array.from(new Set([...prevVal, ...selectionArray])) };
                                  }
                                  return { ...prev, [field]: selectionArray.length === 1 ? selectionArray[0] : selectionArray };
                                } catch (e) { return prev; }
                              });
                              const currentSugs = suggestions;
                              sendMessage(selectionArray).catch(() => {});
                              setSuggestions(currentSugs);
                            }}
                          />
                        );
                        continue;
                      }
                      const filtered = items.filter(it => {
                        const key = (typeof it === 'string') ? it.trim() : it;
                        if (seen.has(key)) return false;
                        seen.add(key);
                        return true;
                      });
                    nodes.push(
                      <SuggestionCard key={field} field={field} items={filtered} disabled={isFetching}
                        contextValues={context?.[field]}
                          onContinue={(sel) => {
                            if (!sel) return;
                            const selectionArray = Array.isArray(sel) ? sel : [sel];
                            setContext(prev => {
                              try {
                                const prevVal = prev?.[field];
                                if (Array.isArray(prevVal)) {
                                  return { ...prev, [field]: Array.from(new Set([...prevVal, ...selectionArray])) };
                                }
                                return { ...prev, [field]: selectionArray.length === 1 ? selectionArray[0] : selectionArray };
                              } catch (e) { return prev; }
                            });
                            const currentSugs = suggestions;
                            sendMessage(selectionArray).catch(() => {});
                            setSuggestions(currentSugs);
                          }}
                        />
                      );
                    }

                    return nodes;
                  })()}
            </div>
          ) : null)}

          <div ref={bottomRef} />
        </div>

        <div className="input-zone">
          <div className="input-card">
            <textarea
              ref={textareaRef}
              className="chat-input"
              placeholder="Type your message here..."
              value={input}
              rows={1}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading || isFetching}
              title="Send (Enter)"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}