-- resources/sql/schema.sql
-- Diyabet Takip Sistemi Veritabanı Şeması

-- Kullanıcı tablosu (doktor ve hastalar için ortak)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tc_id VARCHAR(11) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    birthdate DATE NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('E', 'K')),
    email VARCHAR(255) UNIQUE NOT NULL,
    profile_image BYTEA,
    user_type VARCHAR(10) NOT NULL CHECK (user_type IN ('doctor', 'patient')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Doktor tablosu
CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialty VARCHAR(100),
    hospital VARCHAR(100),
    CONSTRAINT unique_doctor_user_id UNIQUE (user_id)
);

-- Hasta tablosu
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE RESTRICT,
    diagnosis TEXT,
    diabetes_type VARCHAR(20),
    diagnosis_date DATE,
    CONSTRAINT unique_patient_user_id UNIQUE (user_id)
);

-- Ölçüm tablosu
CREATE TABLE IF NOT EXISTS measurements (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    glucose_level NUMERIC(5,1) NOT NULL,
    measurement_date DATE NOT NULL,
    measurement_time TIME NOT NULL,
    period VARCHAR(10) CHECK (period IN ('morning', 'noon', 'afternoon', 'evening', 'night')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Egzersiz tablosu
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    exercise_type VARCHAR(20) NOT NULL CHECK (exercise_type IN ('walking', 'cycling', 'clinical')),
    date DATE NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Diyet tablosu
CREATE TABLE IF NOT EXISTS diets (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    diet_type VARCHAR(20) NOT NULL CHECK (diet_type IN ('low_sugar', 'no_sugar', 'balanced')),
    date DATE NOT NULL,
    is_followed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Belirti tablosu
CREATE TABLE IF NOT EXISTS symptoms (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    symptom_type VARCHAR(20) NOT NULL CHECK (
        symptom_type IN ('polyuria', 'polyphagia', 'polydipsia', 'neuropathy', 
                        'weight_loss', 'fatigue', 'slow_healing', 'blurred_vision')
    ),
    severity INTEGER CHECK (severity BETWEEN 1 AND 5),
    date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Uyarı tablosu
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    alert_type VARCHAR(30) NOT NULL CHECK (
        alert_type IN ('hypoglycemia', 'normal', 'medium_high', 'high', 'hyperglycemia', 
                    'missing_measurement', 'insufficient_measurement')
    ),
    message TEXT NOT NULL,
    glucose_level NUMERIC(5,1),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- İnsülin tablosu
CREATE TABLE IF NOT EXISTS insulins (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    recommended_dose NUMERIC(3,1) NOT NULL,
    administered_dose NUMERIC(3,1),
    average_glucose NUMERIC(5,1),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_measurements_patient_id ON measurements(patient_id);
CREATE INDEX IF NOT EXISTS idx_measurements_date ON measurements(measurement_date);
CREATE INDEX IF NOT EXISTS idx_exercises_patient_id ON exercises(patient_id);
CREATE INDEX IF NOT EXISTS idx_diets_patient_id ON diets(patient_id);
CREATE INDEX IF NOT EXISTS idx_symptoms_patient_id ON symptoms(patient_id);
CREATE INDEX IF NOT EXISTS idx_alerts_patient_id ON alerts(patient_id);
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(patient_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_insulins_patient_id ON insulins(patient_id);
CREATE INDEX IF NOT EXISTS idx_patients_doctor_id ON patients(doctor_id);