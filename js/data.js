/* ============================================
   Mock Data — Patients, Doctors, Medicines, etc.
   ============================================ */
const MockData = {
  patients: [
    { id:'P001', name:'Ramesh Kumar', age:45, gender:'Male', phone:'9876543210', blood:'B+', conditions:['Hypertension','Diabetes Type 2'], allergies:['Penicillin'], avatar:'RK' },
    { id:'P002', name:'Sunita Devi', age:38, gender:'Female', phone:'9123456780', blood:'O+', conditions:['Asthma'], allergies:[], avatar:'SD' },
    { id:'P003', name:'Arjun Singh', age:62, gender:'Male', phone:'9988776655', blood:'A+', conditions:['Arthritis','High Cholesterol'], allergies:['Sulfa'], avatar:'AS' },
    { id:'P004', name:'Priya Sharma', age:29, gender:'Female', phone:'9112233445', blood:'AB-', conditions:[], allergies:['Aspirin'], avatar:'PS' },
    { id:'P005', name:'Mohammed Ali', age:55, gender:'Male', phone:'9334455667', blood:'O-', conditions:['COPD','Diabetes Type 1'], allergies:[], avatar:'MA' },
    { id:'P006', name:'Lakshmi Rao', age:42, gender:'Female', phone:'9556677889', blood:'B-', conditions:['Thyroid'], allergies:['Latex'], avatar:'LR' },
    { id:'P007', name:'Vikram Patel', age:33, gender:'Male', phone:'9778899001', blood:'A-', conditions:[], allergies:[], avatar:'VP' },
    { id:'P008', name:'Ananya Gupta', age:27, gender:'Female', phone:'9900112234', blood:'AB+', conditions:['Migraine'], allergies:['Ibuprofen'], avatar:'AG' },
  ],

  doctors: [
    { id:'D001', name:'Dr. Anjali Mehta', specialization:'Cardiology', qualification:'MD, DM Cardiology', experience:12, available:true, avatar:'AM', rating:4.8, consultations:1847 },
    { id:'D002', name:'Dr. Rajesh Verma', specialization:'General Medicine', qualification:'MBBS, MD Medicine', experience:8, available:true, avatar:'RV', rating:4.6, consultations:2341 },
    { id:'D003', name:'Dr. Suresh Iyer', specialization:'Pulmonology', qualification:'MD, DM Pulmonology', experience:15, available:false, avatar:'SI', rating:4.9, consultations:3102 },
    { id:'D004', name:'Dr. Kavita Nair', specialization:'Dermatology', qualification:'MD Dermatology', experience:6, available:true, avatar:'KN', rating:4.5, consultations:1203 },
    { id:'D005', name:'Dr. Amit Shah', specialization:'Orthopedics', qualification:'MS Orthopedics', experience:10, available:false, avatar:'AS', rating:4.7, consultations:1590 },
    { id:'D006', name:'Dr. Neha Reddy', specialization:'Pediatrics', qualification:'MD Pediatrics', experience:9, available:true, avatar:'NR', rating:4.8, consultations:2089 },
  ],

  medicines: [
    { name:'Amoxicillin', category:'Antibiotic', forms:['Capsule 250mg','Capsule 500mg','Syrup'] },
    { name:'Metformin', category:'Antidiabetic', forms:['Tablet 500mg','Tablet 850mg','Tablet 1000mg'] },
    { name:'Amlodipine', category:'Antihypertensive', forms:['Tablet 2.5mg','Tablet 5mg','Tablet 10mg'] },
    { name:'Atorvastatin', category:'Statin', forms:['Tablet 10mg','Tablet 20mg','Tablet 40mg'] },
    { name:'Omeprazole', category:'PPI', forms:['Capsule 20mg','Capsule 40mg'] },
    { name:'Paracetamol', category:'Analgesic', forms:['Tablet 500mg','Tablet 650mg','Syrup'] },
    { name:'Cetirizine', category:'Antihistamine', forms:['Tablet 10mg','Syrup'] },
    { name:'Salbutamol', category:'Bronchodilator', forms:['Inhaler 100mcg','Nebulizer 2.5mg','Tablet 4mg'] },
    { name:'Losartan', category:'ARB', forms:['Tablet 25mg','Tablet 50mg','Tablet 100mg'] },
    { name:'Montelukast', category:'Leukotriene Inhibitor', forms:['Tablet 4mg','Tablet 10mg'] },
    { name:'Pantoprazole', category:'PPI', forms:['Tablet 20mg','Tablet 40mg'] },
    { name:'Azithromycin', category:'Antibiotic', forms:['Tablet 250mg','Tablet 500mg','Syrup'] },
    { name:'Clopidogrel', category:'Antiplatelet', forms:['Tablet 75mg'] },
    { name:'Levothyroxine', category:'Thyroid', forms:['Tablet 25mcg','Tablet 50mcg','Tablet 100mcg'] },
    { name:'Ibuprofen', category:'NSAID', forms:['Tablet 200mg','Tablet 400mg','Gel'] },
  ],

  departments: ['Cardiology','General Medicine','Pulmonology','Dermatology','Orthopedics','Pediatrics','Neurology','Ophthalmology','ENT','Gynecology'],

  consultationHistory: [
    { id:'C001', patient:'P001', doctor:'D001', date:'2026-05-05', status:'completed', diagnosis:'Essential Hypertension', notes:'BP elevated. Increased Amlodipine dosage.' },
    { id:'C002', patient:'P002', doctor:'D003', date:'2026-05-05', status:'completed', diagnosis:'Acute Bronchitis', notes:'Prescribed bronchodilator + 5-day course.' },
    { id:'C003', patient:'P003', doctor:'D002', date:'2026-05-06', status:'in-progress', diagnosis:'', notes:'' },
    { id:'C004', patient:'P004', doctor:'D004', date:'2026-05-06', status:'waiting', diagnosis:'', notes:'' },
    { id:'C005', patient:'P005', doctor:'D002', date:'2026-05-06', status:'waiting', diagnosis:'', notes:'' },
    { id:'C006', patient:'P006', doctor:'D001', date:'2026-05-06', status:'upcoming', diagnosis:'', notes:'' },
  ],

  healthRecords: [
    { id:'R001', patient:'P001', name:'Blood Test Report', type:'lab', date:'2026-04-28', size:'1.2 MB' },
    { id:'R002', patient:'P001', name:'ECG Report', type:'img', date:'2026-04-20', size:'3.4 MB' },
    { id:'R003', patient:'P001', name:'Prescription - Dr. Mehta', type:'rx', date:'2026-05-05', size:'256 KB' },
    { id:'R004', patient:'P002', name:'Chest X-Ray', type:'img', date:'2026-04-15', size:'5.1 MB' },
    { id:'R005', patient:'P002', name:'Prescription - Dr. Iyer', type:'rx', date:'2026-05-05', size:'198 KB' },
  ],

  analyticsData: {
    dailyConsultations: [42,38,51,47,55,63,58,49,52,61,45,50,67,72,65,58,53,48,44,56,62,70,68,59,55,51,48,63,71,66],
    departmentLoad: {
      'Cardiology': 156,
      'General Medicine': 243,
      'Pulmonology': 89,
      'Dermatology': 112,
      'Orthopedics': 98,
      'Pediatrics': 167,
    },
    weeklyStats: { totalConsultations:342, newPatients:87, avgDuration:'18 min', satisfaction:4.6 }
  },

  rosterSlots: {
    'Cardiology':    ['Dr. Mehta','','Dr. Mehta','','Dr. Mehta',''],
    'General Medicine':['Dr. Verma','Dr. Verma','','Dr. Verma','Dr. Verma',''],
    'Pulmonology':   ['','Dr. Iyer','Dr. Iyer','','Dr. Iyer',''],
    'Dermatology':   ['Dr. Nair','','Dr. Nair','Dr. Nair','','Dr. Nair'],
    'Orthopedics':   ['','Dr. Shah','','Dr. Shah','','Dr. Shah'],
    'Pediatrics':    ['Dr. Reddy','Dr. Reddy','Dr. Reddy','','Dr. Reddy',''],
  }
};
