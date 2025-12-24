# React Form Handling Patterns

## Purpose

This skill provides comprehensive patterns for building robust, accessible, and performant forms in React + TypeScript applications using modern best practices.

**Use this skill when:**
- Building forms with React Hook Form + Zod validation
- Implementing file uploads, multi-step wizards, or complex form flows
- Ensuring form accessibility (ARIA, keyboard navigation)
- Handling async validation, dependent fields, or auto-save
- Optimizing form performance and user experience

**Last Updated:** 2025-12-09

---

## Table of Contents

1. [Form Library Comparison](#1-form-library-comparison)
2. [React Hook Form + Zod Setup](#2-react-hook-form--zod-setup)
3. [Validation Patterns](#3-validation-patterns)
4. [Form State Management](#4-form-state-management)
5. [File Upload Patterns](#5-file-upload-patterns)
6. [Multi-Step Forms](#6-multi-step-forms)
7. [Form Accessibility](#7-form-accessibility)
8. [Async Validation](#8-async-validation)
9. [Dependent Fields](#9-dependent-fields)
10. [Auto-Save Drafts](#10-auto-save-drafts)
11. [Submit Error Handling](#11-submit-error-handling)
12. [Performance Optimization](#12-performance-optimization)
13. [Common Anti-Patterns](#13-common-anti-patterns)
14. [Summary](#summary)

---

## 1. Form Library Comparison

### Problem
Choosing the right form library impacts performance, developer experience, and bundle size.

### Solution
Use **React Hook Form** for most use cases in 2025. It offers the best combination of performance, TypeScript support, and developer experience.

### Comparison Table

| Feature | React Hook Form | Formik | Native Forms |
|---------|----------------|--------|--------------|
| **Bundle Size** | ~9KB | ~13KB | 0KB |
| **Re-renders** | Minimal (isolated) | Whole form | Manual control |
| **TypeScript** | Excellent | Good | Manual |
| **Performance** | Excellent | Good | Excellent |
| **DX** | Excellent | Good | Poor |
| **Validation** | Schema-based | Schema-based | Manual |
| **Learning Curve** | Low | Medium | Low |
| **Use Case** | Most forms | Legacy projects | Simple forms |

### When to Use Each

**React Hook Form:**
- ✅ New projects
- ✅ Complex forms with many fields
- ✅ Performance-critical applications
- ✅ TypeScript projects

**Formik:**
- ✅ Existing Formik codebases
- ✅ Teams familiar with Formik

**Native Forms:**
- ✅ Extremely simple forms (1-3 fields)
- ✅ Server-side rendered forms
- ✅ Zero-dependency requirements

### Anti-Pattern

❌ **WRONG: Using state for every form field**
```tsx
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [name, setName] = useState('');
// 20+ more fields...
// Result: Component re-renders on every keystroke
```

✅ **CORRECT: Using React Hook Form**
```tsx
const { register, handleSubmit } = useForm<FormData>();
// Result: Minimal re-renders, better performance
```

---

## 2. React Hook Form + Zod Setup

### Problem
Need type-safe form validation with minimal boilerplate.

### Solution
Combine React Hook Form with Zod for schema-based validation and automatic TypeScript type inference.

### Implementation

**Step 1: Install Dependencies**
```bash
npm install react-hook-form zod @hookform/resolvers
```

**Step 2: Define Schema**
```tsx
import { z } from 'zod';

// Define validation schema
const userSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  age: z.number().min(18, 'Must be 18 or older').optional(),
  terms: z.boolean().refine((val) => val === true, {
    message: 'You must accept the terms',
  }),
});

// Automatically infer TypeScript type
type UserFormData = z.infer<typeof userSchema>;
```

**Step 3: Create Form Component**
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

export function UserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      email: '',
      password: '',
      terms: false,
    },
  });

  const onSubmit = async (data: UserFormData) => {
    try {
      await api.createUser(data);
      toast.success('User created!');
    } catch (error) {
      toast.error('Failed to create user');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className="mt-1 block w-full rounded-md border-gray-300"
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <p id="email-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.email.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          type="password"
          {...register('password')}
          className="mt-1 block w-full rounded-md border-gray-300"
          aria-invalid={errors.password ? 'true' : 'false'}
          aria-describedby={errors.password ? 'password-error' : undefined}
        />
        {errors.password && (
          <p id="password-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.password.message}
          </p>
        )}
      </div>

      <div className="flex items-center">
        <input
          id="terms"
          type="checkbox"
          {...register('terms')}
          className="h-4 w-4 rounded border-gray-300"
          aria-invalid={errors.terms ? 'true' : 'false'}
          aria-describedby={errors.terms ? 'terms-error' : undefined}
        />
        <label htmlFor="terms" className="ml-2 text-sm">
          I accept the terms and conditions
        </label>
      </div>
      {errors.terms && (
        <p id="terms-error" className="text-sm text-red-600" role="alert">
          {errors.terms.message}
        </p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
      >
        {isSubmitting ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

### Anti-Pattern

❌ **WRONG: Manually validating each field**
```tsx
const validateEmail = (email: string) => {
  if (!email) return 'Email required';
  if (!email.includes('@')) return 'Invalid email';
  // Manual validation for every field
};
```

✅ **CORRECT: Schema-based validation with Zod**
```tsx
const schema = z.object({
  email: z.string().email('Invalid email'),
  // Single source of truth for validation + types
});
```

---

## 3. Validation Patterns

### Problem
Need comprehensive validation covering sync/async, client/server, and custom rules.

### Solution
Use Zod's rich schema API for complex validation scenarios.

### Implementation

**Complex Validation Schema**
```tsx
import { z } from 'zod';

const profileSchema = z.object({
  // Basic validation
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must be at most 20 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),

  // Email validation
  email: z.string().email('Invalid email address'),

  // Password with custom rules
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),

  // Confirm password
  confirmPassword: z.string(),

  // Optional fields
  bio: z.string().max(500, 'Bio must be at most 500 characters').optional(),

  // Number validation
  age: z.number().int().min(18, 'Must be 18 or older').max(120, 'Invalid age'),

  // Enum validation
  role: z.enum(['user', 'admin', 'moderator'], {
    errorMap: () => ({ message: 'Invalid role' }),
  }),

  // Array validation
  tags: z
    .array(z.string())
    .min(1, 'At least one tag required')
    .max(5, 'Maximum 5 tags allowed'),

  // Date validation
  birthDate: z.date().max(new Date(), 'Birth date cannot be in the future'),

  // URL validation
  website: z.string().url('Invalid URL').optional(),

  // Custom validation
  phoneNumber: z
    .string()
    .regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number')
    .optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'], // Set error on confirmPassword field
});

type ProfileFormData = z.infer<typeof profileSchema>;
```

**Conditional Validation**
```tsx
const addressSchema = z.object({
  country: z.string(),
  state: z.string().optional(),
  postalCode: z.string(),
}).refine(
  (data) => {
    // Require state for US addresses
    if (data.country === 'US' && !data.state) {
      return false;
    }
    return true;
  },
  {
    message: 'State is required for US addresses',
    path: ['state'],
  }
);
```

**Dependent Field Validation**
```tsx
const shippingSchema = z.object({
  sameAsBilling: z.boolean(),
  shippingAddress: z.string().optional(),
}).refine(
  (data) => {
    // Require shipping address if different from billing
    if (!data.sameAsBilling && !data.shippingAddress) {
      return false;
    }
    return true;
  },
  {
    message: 'Shipping address is required',
    path: ['shippingAddress'],
  }
);
```

**Union Schemas (Discriminated Unions)**
```tsx
const paymentSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('credit_card'),
    cardNumber: z.string().regex(/^\d{16}$/, 'Invalid card number'),
    cvv: z.string().regex(/^\d{3,4}$/, 'Invalid CVV'),
    expiryDate: z.string().regex(/^\d{2}\/\d{2}$/, 'Invalid expiry date (MM/YY)'),
  }),
  z.object({
    type: z.literal('paypal'),
    email: z.string().email('Invalid PayPal email'),
  }),
  z.object({
    type: z.literal('bank_transfer'),
    accountNumber: z.string().min(8, 'Invalid account number'),
    routingNumber: z.string().length(9, 'Routing number must be 9 digits'),
  }),
]);
```

### Anti-Pattern

❌ **WRONG: Scattered validation logic**
```tsx
// Validation in multiple places
const handleSubmit = (data) => {
  if (!data.email.includes('@')) {
    setError('Invalid email');
    return;
  }
  if (data.password.length < 8) {
    setError('Password too short');
    return;
  }
  // Hard to maintain, no TypeScript inference
};
```

✅ **CORRECT: Centralized schema validation**
```tsx
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});
// Single source of truth, automatic TypeScript types
```

---

## 4. Form State Management

### Problem
Choose between controlled vs uncontrolled components, handle field arrays and dynamic fields.

### Solution
React Hook Form uses **uncontrolled components** by default for better performance, with support for controlled components when needed.

### Controlled vs Uncontrolled

**Uncontrolled (Recommended)**
```tsx
import { useForm } from 'react-hook-form';

function UncontrolledForm() {
  const { register, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Uncontrolled: No value prop, uses ref */}
      <input {...register('email')} />
      <input {...register('password')} />
    </form>
  );
}
```

**Controlled (When Needed)**
```tsx
import { useForm, Controller } from 'react-hook-form';
import Select from 'react-select'; // Third-party component

function ControlledForm() {
  const { control, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Controlled: For third-party components */}
      <Controller
        name="country"
        control={control}
        render={({ field }) => (
          <Select
            {...field}
            options={countryOptions}
            onChange={(option) => field.onChange(option?.value)}
          />
        )}
      />
    </form>
  );
}
```

### Field Arrays (Dynamic Fields)

**Problem:** Handle dynamic lists of items (e.g., phone numbers, addresses).

**Solution:** Use `useFieldArray` for optimized performance.

```tsx
import { useForm, useFieldArray } from 'react-hook-form';
import { z } from 'zod';

const contactSchema = z.object({
  name: z.string().min(1, 'Name required'),
  phoneNumbers: z.array(
    z.object({
      type: z.enum(['mobile', 'home', 'work']),
      number: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number'),
    })
  ).min(1, 'At least one phone number required'),
});

type ContactFormData = z.infer<typeof contactSchema>;

function ContactForm() {
  const { register, control, handleSubmit, formState: { errors } } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      name: '',
      phoneNumbers: [{ type: 'mobile', number: '' }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'phoneNumbers',
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" {...register('name')} />
        {errors.name && <p className="error">{errors.name.message}</p>}
      </div>

      <div>
        <label className="block font-medium mb-2">Phone Numbers</label>
        {fields.map((field, index) => (
          <div key={field.id} className="flex gap-2 mb-2">
            <select {...register(`phoneNumbers.${index}.type` as const)}>
              <option value="mobile">Mobile</option>
              <option value="home">Home</option>
              <option value="work">Work</option>
            </select>

            <input
              {...register(`phoneNumbers.${index}.number` as const)}
              placeholder="Phone number"
              className="flex-1"
            />

            <button
              type="button"
              onClick={() => remove(index)}
              disabled={fields.length === 1}
              className="px-2 py-1 bg-red-500 text-white rounded disabled:opacity-50"
            >
              Remove
            </button>
          </div>
        ))}

        {errors.phoneNumbers && (
          <p className="error">{errors.phoneNumbers.message}</p>
        )}

        <button
          type="button"
          onClick={() => append({ type: 'mobile', number: '' })}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
        >
          Add Phone Number
        </button>
      </div>

      <button type="submit">Submit</button>
    </form>
  );
}
```

### Nested Objects

```tsx
const addressFormSchema = z.object({
  personal: z.object({
    firstName: z.string().min(1),
    lastName: z.string().min(1),
  }),
  address: z.object({
    street: z.string().min(1),
    city: z.string().min(1),
    postalCode: z.string().min(1),
  }),
});

function NestedForm() {
  const { register, handleSubmit } = useForm<z.infer<typeof addressFormSchema>>({
    resolver: zodResolver(addressFormSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('personal.firstName')} placeholder="First Name" />
      <input {...register('personal.lastName')} placeholder="Last Name" />

      <input {...register('address.street')} placeholder="Street" />
      <input {...register('address.city')} placeholder="City" />
      <input {...register('address.postalCode')} placeholder="Postal Code" />

      <button type="submit">Submit</button>
    </form>
  );
}
```

### Anti-Pattern

❌ **WRONG: Manual array state management**
```tsx
const [items, setItems] = useState([{ value: '' }]);

const addItem = () => {
  setItems([...items, { value: '' }]);
  // No validation, no type safety, causes full re-renders
};
```

✅ **CORRECT: useFieldArray**
```tsx
const { fields, append } = useFieldArray({ control, name: 'items' });
append({ value: '' });
// Type-safe, validated, optimized re-renders
```

---

## 5. File Upload Patterns

### Problem
Handle file uploads with drag-and-drop, progress tracking, validation, and preview.

### Solution
Use **react-dropzone** with React Hook Form for a complete file upload solution.

### Implementation

**Step 1: Install Dependencies**
```bash
npm install react-dropzone
```

**Step 2: Create File Upload Component**
```tsx
import { useCallback, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useDropzone, FileRejection } from 'react-dropzone';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

// Custom Zod validator for files
const fileSchema = z.custom<File>((val) => val instanceof File, {
  message: 'Required',
});

const uploadSchema = z.object({
  avatar: fileSchema
    .refine((file) => file.size <= 5 * 1024 * 1024, 'File must be less than 5MB')
    .refine(
      (file) => ['image/jpeg', 'image/png', 'image/webp'].includes(file.type),
      'Only JPEG, PNG, and WebP images are allowed'
    ),
  documents: z
    .array(fileSchema)
    .min(1, 'At least one document required')
    .max(5, 'Maximum 5 documents allowed'),
});

type UploadFormData = z.infer<typeof uploadSchema>;

function FileUploadForm() {
  const [preview, setPreview] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  const {
    control,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<UploadFormData>({
    resolver: zodResolver(uploadSchema),
  });

  const onSubmit = async (data: UploadFormData) => {
    const formData = new FormData();
    formData.append('avatar', data.avatar);
    data.documents.forEach((doc) => formData.append('documents', doc));

    // Use XMLHttpRequest for progress tracking (fetch doesn't support upload progress)
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setUploadProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          resolve(xhr.response);
        } else {
          reject(new Error('Upload failed'));
        }
      });

      xhr.addEventListener('error', () => reject(new Error('Upload failed')));

      xhr.open('POST', '/api/upload');
      xhr.send(formData);
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Avatar Upload with Preview */}
      <div>
        <label className="block text-sm font-medium mb-2">Avatar</label>
        <Controller
          name="avatar"
          control={control}
          render={({ field: { onChange, value } }) => (
            <AvatarDropzone
              onDrop={(file) => {
                onChange(file);
                // Create preview
                const reader = new FileReader();
                reader.onloadend = () => setPreview(reader.result as string);
                reader.readAsDataURL(file);
              }}
              preview={preview}
            />
          )}
        />
        {errors.avatar && (
          <p className="mt-1 text-sm text-red-600">{errors.avatar.message}</p>
        )}
      </div>

      {/* Multiple File Upload */}
      <div>
        <label className="block text-sm font-medium mb-2">Documents</label>
        <Controller
          name="documents"
          control={control}
          render={({ field: { onChange, value = [] } }) => (
            <DocumentDropzone onDrop={onChange} files={value} />
          )}
        />
        {errors.documents && (
          <p className="mt-1 text-sm text-red-600">{errors.documents.message}</p>
        )}
      </div>

      {/* Progress Bar */}
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
      )}

      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Upload Files
      </button>
    </form>
  );
}

// Avatar Dropzone Component
function AvatarDropzone({
  onDrop,
  preview,
}: {
  onDrop: (file: File) => void;
  preview: string | null;
}) {
  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onDrop(acceptedFiles[0]);
      }
    },
    [onDrop]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop: handleDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
    },
    maxSize: 5 * 1024 * 1024, // 5MB
    multiple: false,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        `}
      >
        <input {...getInputProps()} />
        {preview ? (
          <div className="space-y-2">
            <img
              src={preview}
              alt="Preview"
              className="mx-auto h-32 w-32 object-cover rounded-full"
            />
            <p className="text-sm text-gray-600">Click or drag to replace</p>
          </div>
        ) : (
          <div className="space-y-2">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="text-sm text-gray-600">
              {isDragActive ? 'Drop the image here' : 'Drag & drop or click to select'}
            </p>
            <p className="text-xs text-gray-500">JPEG, PNG, or WebP (max 5MB)</p>
          </div>
        )}
      </div>

      {fileRejections.length > 0 && (
        <div className="mt-2 text-sm text-red-600">
          {fileRejections[0].errors[0].message}
        </div>
      )}
    </div>
  );
}

// Document Dropzone Component
function DocumentDropzone({
  onDrop,
  files,
}: {
  onDrop: (files: File[]) => void;
  files: File[];
}) {
  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      onDrop([...files, ...acceptedFiles]);
    },
    [files, onDrop]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = (index: number) => {
    onDrop(files.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        `}
      >
        <input {...getInputProps()} />
        <p className="text-sm text-gray-600">
          {isDragActive ? 'Drop files here' : 'Drag & drop documents or click to select'}
        </p>
        <p className="text-xs text-gray-500 mt-1">PDF, DOC, DOCX (max 10MB each)</p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((file, index) => (
            <li
              key={index}
              className="flex items-center justify-between p-2 bg-gray-50 rounded"
            >
              <div className="flex items-center space-x-2">
                <svg
                  className="h-5 w-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="text-red-600 hover:text-red-800"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Anti-Pattern

❌ **WRONG: Using fetch() for upload progress**
```tsx
// fetch() doesn't support upload progress
const response = await fetch('/upload', {
  method: 'POST',
  body: formData,
});
// No way to track progress!
```

✅ **CORRECT: XMLHttpRequest for progress**
```tsx
const xhr = new XMLHttpRequest();
xhr.upload.addEventListener('progress', (e) => {
  const progress = (e.loaded / e.total) * 100;
  setUploadProgress(progress);
});
xhr.send(formData);
```

---

## 6. Multi-Step Forms

### Problem
Build wizard-style forms with multiple steps, state persistence, and navigation.

### Solution
Use React Hook Form with state management for current step and form data persistence.

### Implementation

**Step 1: Define Schema for Each Step**
```tsx
import { z } from 'zod';

// Step 1: Personal Info
const step1Schema = z.object({
  firstName: z.string().min(1, 'First name required'),
  lastName: z.string().min(1, 'Last name required'),
  email: z.string().email('Invalid email'),
});

// Step 2: Address
const step2Schema = z.object({
  street: z.string().min(1, 'Street required'),
  city: z.string().min(1, 'City required'),
  postalCode: z.string().min(1, 'Postal code required'),
  country: z.string().min(1, 'Country required'),
});

// Step 3: Preferences
const step3Schema = z.object({
  newsletter: z.boolean(),
  notifications: z.boolean(),
  theme: z.enum(['light', 'dark', 'auto']),
});

// Combined schema for final validation
const fullSchema = step1Schema.merge(step2Schema).merge(step3Schema);

type FormData = z.infer<typeof fullSchema>;
type Step1Data = z.infer<typeof step1Schema>;
type Step2Data = z.infer<typeof step2Schema>;
type Step3Data = z.infer<typeof step3Schema>;
```

**Step 2: Create Multi-Step Form Component**
```tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

function MultiStepForm() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<Partial<FormData>>({});

  const goToNext = (data: Partial<FormData>) => {
    setFormData((prev) => ({ ...prev, ...data }));
    setCurrentStep((prev) => prev + 1);
  };

  const goToPrevious = () => {
    setCurrentStep((prev) => prev - 1);
  };

  const onFinalSubmit = async (data: Partial<FormData>) => {
    const fullData = { ...formData, ...data } as FormData;

    try {
      await api.submitForm(fullData);
      toast.success('Form submitted successfully!');
    } catch (error) {
      toast.error('Failed to submit form');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {[1, 2, 3].map((step) => (
            <div
              key={step}
              className={`
                flex-1 text-center pb-2 border-b-2 transition-colors
                ${step === currentStep ? 'border-blue-600 text-blue-600' : ''}
                ${step < currentStep ? 'border-green-600 text-green-600' : ''}
                ${step > currentStep ? 'border-gray-300 text-gray-400' : ''}
              `}
            >
              <div className="font-medium">Step {step}</div>
              <div className="text-xs mt-1">
                {step === 1 && 'Personal Info'}
                {step === 2 && 'Address'}
                {step === 3 && 'Preferences'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Form Steps */}
      {currentStep === 1 && (
        <Step1Form
          defaultValues={formData}
          onNext={goToNext}
        />
      )}
      {currentStep === 2 && (
        <Step2Form
          defaultValues={formData}
          onNext={goToNext}
          onPrevious={goToPrevious}
        />
      )}
      {currentStep === 3 && (
        <Step3Form
          defaultValues={formData}
          onSubmit={onFinalSubmit}
          onPrevious={goToPrevious}
        />
      )}
    </div>
  );
}

// Step 1: Personal Info
function Step1Form({
  defaultValues,
  onNext,
}: {
  defaultValues: Partial<FormData>;
  onNext: (data: Step1Data) => void;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
    defaultValues,
  });

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Personal Information</h2>

      <div>
        <label htmlFor="firstName" className="block text-sm font-medium mb-1">
          First Name
        </label>
        <input
          id="firstName"
          {...register('firstName')}
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.firstName && (
          <p className="mt-1 text-sm text-red-600">{errors.firstName.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="lastName" className="block text-sm font-medium mb-1">
          Last Name
        </label>
        <input
          id="lastName"
          {...register('lastName')}
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.lastName && (
          <p className="mt-1 text-sm text-red-600">{errors.lastName.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Next
        </button>
      </div>
    </form>
  );
}

// Step 2: Address (similar structure)
function Step2Form({
  defaultValues,
  onNext,
  onPrevious,
}: {
  defaultValues: Partial<FormData>;
  onNext: (data: Step2Data) => void;
  onPrevious: () => void;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Step2Data>({
    resolver: zodResolver(step2Schema),
    defaultValues,
  });

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Address</h2>

      <div>
        <label htmlFor="street" className="block text-sm font-medium mb-1">
          Street Address
        </label>
        <input
          id="street"
          {...register('street')}
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.street && (
          <p className="mt-1 text-sm text-red-600">{errors.street.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="city" className="block text-sm font-medium mb-1">
            City
          </label>
          <input
            id="city"
            {...register('city')}
            className="w-full px-3 py-2 border rounded-md"
          />
          {errors.city && (
            <p className="mt-1 text-sm text-red-600">{errors.city.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="postalCode" className="block text-sm font-medium mb-1">
            Postal Code
          </label>
          <input
            id="postalCode"
            {...register('postalCode')}
            className="w-full px-3 py-2 border rounded-md"
          />
          {errors.postalCode && (
            <p className="mt-1 text-sm text-red-600">{errors.postalCode.message}</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="country" className="block text-sm font-medium mb-1">
          Country
        </label>
        <select
          id="country"
          {...register('country')}
          className="w-full px-3 py-2 border rounded-md"
        >
          <option value="">Select a country</option>
          <option value="US">United States</option>
          <option value="CA">Canada</option>
          <option value="UK">United Kingdom</option>
        </select>
        {errors.country && (
          <p className="mt-1 text-sm text-red-600">{errors.country.message}</p>
        )}
      </div>

      <div className="flex justify-between">
        <button
          type="button"
          onClick={onPrevious}
          className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Previous
        </button>
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Next
        </button>
      </div>
    </form>
  );
}

// Step 3: Preferences (final step)
function Step3Form({
  defaultValues,
  onSubmit,
  onPrevious,
}: {
  defaultValues: Partial<FormData>;
  onSubmit: (data: Step3Data) => void;
  onPrevious: () => void;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Step3Data>({
    resolver: zodResolver(step3Schema),
    defaultValues: {
      newsletter: defaultValues.newsletter ?? false,
      notifications: defaultValues.notifications ?? true,
      theme: defaultValues.theme ?? 'auto',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Preferences</h2>

      <div className="space-y-3">
        <label className="flex items-center">
          <input
            type="checkbox"
            {...register('newsletter')}
            className="h-4 w-4 rounded border-gray-300"
          />
          <span className="ml-2 text-sm">Subscribe to newsletter</span>
        </label>

        <label className="flex items-center">
          <input
            type="checkbox"
            {...register('notifications')}
            className="h-4 w-4 rounded border-gray-300"
          />
          <span className="ml-2 text-sm">Enable notifications</span>
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Theme</label>
        <div className="space-y-2">
          {(['light', 'dark', 'auto'] as const).map((option) => (
            <label key={option} className="flex items-center">
              <input
                type="radio"
                value={option}
                {...register('theme')}
                className="h-4 w-4"
              />
              <span className="ml-2 text-sm capitalize">{option}</span>
            </label>
          ))}
        </div>
        {errors.theme && (
          <p className="mt-1 text-sm text-red-600">{errors.theme.message}</p>
        )}
      </div>

      <div className="flex justify-between">
        <button
          type="button"
          onClick={onPrevious}
          className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Previous
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </button>
      </div>
    </form>
  );
}
```

### State Persistence with localStorage

```tsx
function MultiStepFormWithPersistence() {
  const [currentStep, setCurrentStep] = useState(() => {
    const saved = localStorage.getItem('formStep');
    return saved ? parseInt(saved, 10) : 1;
  });

  const [formData, setFormData] = useState<Partial<FormData>>(() => {
    const saved = localStorage.getItem('formData');
    return saved ? JSON.parse(saved) : {};
  });

  useEffect(() => {
    localStorage.setItem('formStep', currentStep.toString());
  }, [currentStep]);

  useEffect(() => {
    localStorage.setItem('formData', JSON.stringify(formData));
  }, [formData]);

  const clearDraft = () => {
    localStorage.removeItem('formStep');
    localStorage.removeItem('formData');
    setCurrentStep(1);
    setFormData({});
  };

  // ... rest of implementation
}
```

### Anti-Pattern

❌ **WRONG: Separate forms without state sharing**
```tsx
// Each step has its own form, data is lost
<Step1 onNext={() => setStep(2)} />
<Step2 onNext={() => setStep(3)} />
// No way to combine data from all steps
```

✅ **CORRECT: Shared state across steps**
```tsx
const [formData, setFormData] = useState({});
const goToNext = (data) => {
  setFormData((prev) => ({ ...prev, ...data }));
  setCurrentStep((prev) => prev + 1);
};
```

---

## 7. Form Accessibility

### Problem
Ensure forms are usable by all users, including those with disabilities.

### Solution
Follow ARIA patterns, keyboard navigation standards, and screen reader best practices.

### Implementation

**Accessible Form Component**
```tsx
import { useForm } from 'react-hook-form';
import { useId } from 'react';

function AccessibleForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm();

  // Generate unique IDs for each field
  const emailId = useId();
  const emailErrorId = useId();
  const passwordId = useId();
  const passwordErrorId = useId();

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      aria-label="Login form"
      noValidate // Use custom validation instead of browser default
    >
      <fieldset className="space-y-4">
        <legend className="text-2xl font-bold mb-4">Sign In</legend>

        {/* Email Field */}
        <div>
          <label
            htmlFor={emailId}
            className="block text-sm font-medium mb-1"
          >
            Email Address
            <span aria-label="required" className="text-red-600">
              {' '}*
            </span>
          </label>
          <input
            id={emailId}
            type="email"
            {...register('email', { required: 'Email is required' })}
            className={`
              w-full px-3 py-2 border rounded-md
              ${errors.email ? 'border-red-500' : 'border-gray-300'}
            `}
            aria-invalid={errors.email ? 'true' : 'false'}
            aria-describedby={errors.email ? emailErrorId : undefined}
            aria-required="true"
          />
          {errors.email && (
            <p
              id={emailErrorId}
              className="mt-1 text-sm text-red-600"
              role="alert"
              aria-live="polite"
            >
              <span className="sr-only">Error: </span>
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password Field */}
        <div>
          <label
            htmlFor={passwordId}
            className="block text-sm font-medium mb-1"
          >
            Password
            <span aria-label="required" className="text-red-600">
              {' '}*
            </span>
          </label>
          <input
            id={passwordId}
            type="password"
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters',
              },
            })}
            className={`
              w-full px-3 py-2 border rounded-md
              ${errors.password ? 'border-red-500' : 'border-gray-300'}
            `}
            aria-invalid={errors.password ? 'true' : 'false'}
            aria-describedby={errors.password ? passwordErrorId : undefined}
            aria-required="true"
          />
          {errors.password && (
            <p
              id={passwordErrorId}
              className="mt-1 text-sm text-red-600"
              role="alert"
              aria-live="polite"
            >
              <span className="sr-only">Error: </span>
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="
            w-full px-4 py-2 bg-blue-600 text-white rounded-md
            hover:bg-blue-700 focus:outline-none focus:ring-2
            focus:ring-blue-500 focus:ring-offset-2
            disabled:opacity-50 disabled:cursor-not-allowed
          "
          aria-busy={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <span className="sr-only">Signing in, please wait</span>
              <span aria-hidden="true">Signing in...</span>
            </>
          ) : (
            'Sign In'
          )}
        </button>
      </fieldset>
    </form>
  );
}
```

### Keyboard Navigation Patterns

**Tab Order and Focus Management**
```tsx
import { useRef } from 'react';

function FormWithFocusManagement() {
  const firstErrorRef = useRef<HTMLInputElement>(null);

  const onSubmit = async (data: FormData) => {
    try {
      await api.submit(data);
    } catch (error) {
      // Focus first error field
      firstErrorRef.current?.focus();
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email')}
        ref={errors.email ? firstErrorRef : undefined}
        onKeyDown={(e) => {
          // Submit on Enter key
          if (e.key === 'Enter' && !e.shiftKey) {
            handleSubmit(onSubmit)(e);
          }
        }}
      />
      {/* More fields */}
    </form>
  );
}
```

**Accessible Custom Select**
```tsx
import { useState, useRef, useEffect } from 'react';
import { Controller } from 'react-hook-form';

interface Option {
  value: string;
  label: string;
}

function AccessibleSelect({
  options,
  value,
  onChange,
  label,
  id,
}: {
  options: Option[];
  value: string;
  onChange: (value: string) => void;
  label: string;
  id: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listboxRef = useRef<HTMLUListElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (isOpen) {
          onChange(options[activeIndex].value);
          setIsOpen(false);
        } else {
          setIsOpen(true);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        buttonRef.current?.focus();
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setActiveIndex((prev) => (prev + 1) % options.length);
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setActiveIndex((prev) => (prev - 1 + options.length) % options.length);
        }
        break;
      case 'Home':
        e.preventDefault();
        setActiveIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setActiveIndex(options.length - 1);
        break;
    }
  };

  const selectedOption = options.find((opt) => opt.value === value);

  return (
    <div className="relative">
      <label id={`${id}-label`} className="block text-sm font-medium mb-1">
        {label}
      </label>
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        aria-labelledby={`${id}-label`}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        className="w-full px-3 py-2 text-left border rounded-md"
      >
        {selectedOption?.label || 'Select an option'}
      </button>

      {isOpen && (
        <ul
          ref={listboxRef}
          role="listbox"
          aria-labelledby={`${id}-label`}
          aria-activedescendant={`${id}-option-${activeIndex}`}
          className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto"
        >
          {options.map((option, index) => (
            <li
              key={option.value}
              id={`${id}-option-${index}`}
              role="option"
              aria-selected={option.value === value}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
                buttonRef.current?.focus();
              }}
              className={`
                px-3 py-2 cursor-pointer
                ${index === activeIndex ? 'bg-blue-100' : ''}
                ${option.value === value ? 'bg-blue-50 font-medium' : ''}
              `}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Accessibility Checklist

**Essential ARIA Attributes:**
- ✅ `aria-label` or `aria-labelledby` on form elements
- ✅ `aria-invalid="true"` on fields with errors
- ✅ `aria-describedby` to link error messages
- ✅ `aria-required="true"` for required fields
- ✅ `role="alert"` or `aria-live="polite"` for error messages
- ✅ `aria-busy="true"` on submit button during submission

**Keyboard Navigation:**
- ✅ Tab to move forward through fields
- ✅ Shift+Tab to move backward
- ✅ Enter to submit form
- ✅ Escape to close dialogs/dropdowns
- ✅ Arrow keys for radio groups, selects

**Visual Indicators:**
- ✅ Clear focus states (outline or ring)
- ✅ Color contrast ratio ≥ 4.5:1 for text
- ✅ Don't rely on color alone for errors
- ✅ Large touch targets (≥44x44px)

### Anti-Pattern

❌ **WRONG: Inaccessible error messages**
```tsx
{errors.email && <p>Invalid email</p>}
// No connection to input, screen readers can't announce
```

✅ **CORRECT: Connected error messages**
```tsx
<input
  aria-invalid={!!errors.email}
  aria-describedby={errors.email ? 'email-error' : undefined}
/>
{errors.email && (
  <p id="email-error" role="alert">
    {errors.email.message}
  </p>
)}
```

---

## 8. Async Validation

### Problem
Validate fields against server (e.g., username availability, email uniqueness).

### Solution
Use React Hook Form's async validation with debouncing to avoid excessive API calls.

### Implementation

**Debounced Async Validation**
```tsx
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { debounce } from 'lodash-es';
import { useCallback, useMemo } from 'react';

// API function
async function checkUsernameAvailability(username: string): Promise<boolean> {
  const response = await fetch(`/api/check-username?username=${username}`);
  const data = await response.json();
  return data.available;
}

const schema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must be at most 20 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
  email: z.string().email('Invalid email'),
});

type FormData = z.infer<typeof schema>;

function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isValidating },
    setError,
    clearErrors,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    mode: 'onBlur', // Validate on blur to avoid constant validation
  });

  // Debounced username check
  const checkUsername = useMemo(
    () =>
      debounce(async (username: string) => {
        if (username.length < 3) return;

        try {
          const available = await checkUsernameAvailability(username);
          if (!available) {
            setError('username', {
              type: 'manual',
              message: 'Username is already taken',
            });
          } else {
            clearErrors('username');
          }
        } catch (error) {
          console.error('Failed to check username:', error);
        }
      }, 500), // 500ms debounce
    [setError, clearErrors]
  );

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    checkUsername(value);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="username" className="block text-sm font-medium mb-1">
          Username
        </label>
        <div className="relative">
          <input
            id="username"
            {...register('username', {
              onChange: handleUsernameChange,
            })}
            className="w-full px-3 py-2 border rounded-md"
            aria-invalid={errors.username ? 'true' : 'false'}
            aria-describedby={errors.username ? 'username-error' : undefined}
          />
          {isValidating && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <svg
                className="animate-spin h-5 w-5 text-blue-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
          )}
        </div>
        {errors.username && (
          <p id="username-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.username.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Sign Up
      </button>
    </form>
  );
}
```

**Alternative: Using trigger() API**
```tsx
import { useForm } from 'react-hook-form';
import { debounce } from 'lodash-es';

function FormWithTrigger() {
  const {
    register,
    handleSubmit,
    trigger,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  // Debounced validation trigger
  const debouncedValidate = useMemo(
    () =>
      debounce(async (fieldName: keyof FormData) => {
        await trigger(fieldName);
      }, 300),
    [trigger]
  );

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('username')}
        onChange={(e) => {
          // Manually trigger validation after debounce
          debouncedValidate('username');
        }}
      />
      {errors.username && <p>{errors.username.message}</p>}
    </form>
  );
}
```

### Anti-Pattern

❌ **WRONG: No debouncing**
```tsx
const checkUsername = async (username: string) => {
  const available = await api.checkUsername(username);
  // API call on every keystroke!
};

<input
  onChange={(e) => checkUsername(e.target.value)}
/>
```

✅ **CORRECT: Debounced validation**
```tsx
const checkUsername = useMemo(
  () => debounce(async (username: string) => {
    await api.checkUsername(username);
  }, 500),
  []
);
```

---

## 9. Dependent Fields

### Problem
Show/hide or validate fields based on other field values.

### Solution
Use React Hook Form's `watch` API for conditional rendering and validation.

### Implementation

**Basic Conditional Rendering**
```tsx
import { useForm } from 'react-hook-form';

function ConditionalForm() {
  const { register, watch, handleSubmit } = useForm();

  // Watch specific field
  const hasCompany = watch('hasCompany');
  const country = watch('country');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="flex items-center">
          <input type="checkbox" {...register('hasCompany')} />
          <span className="ml-2">I represent a company</span>
        </label>
      </div>

      {/* Conditionally render company fields */}
      {hasCompany && (
        <>
          <div>
            <label htmlFor="companyName">Company Name</label>
            <input
              id="companyName"
              {...register('companyName', {
                required: hasCompany ? 'Company name required' : false,
              })}
            />
          </div>

          <div>
            <label htmlFor="taxId">Tax ID</label>
            <input
              id="taxId"
              {...register('taxId', {
                required: hasCompany ? 'Tax ID required' : false,
              })}
            />
          </div>
        </>
      )}

      <div>
        <label htmlFor="country">Country</label>
        <select id="country" {...register('country')}>
          <option value="">Select country</option>
          <option value="US">United States</option>
          <option value="CA">Canada</option>
          <option value="UK">United Kingdom</option>
        </select>
      </div>

      {/* Show state field only for US */}
      {country === 'US' && (
        <div>
          <label htmlFor="state">State</label>
          <select
            id="state"
            {...register('state', {
              required: country === 'US' ? 'State required for US' : false,
            })}
          >
            <option value="">Select state</option>
            <option value="CA">California</option>
            <option value="NY">New York</option>
            <option value="TX">Texas</option>
          </select>
        </div>
      )}

      <button type="submit">Submit</button>
    </form>
  );
}
```

**With Zod Schema**
```tsx
import { z } from 'zod';

// Dynamic schema based on field values
const createSchema = (hasCompany: boolean, country: string) => {
  return z.object({
    hasCompany: z.boolean(),
    companyName: hasCompany
      ? z.string().min(1, 'Company name required')
      : z.string().optional(),
    taxId: hasCompany
      ? z.string().min(1, 'Tax ID required')
      : z.string().optional(),
    country: z.string().min(1, 'Country required'),
    state: country === 'US'
      ? z.string().min(1, 'State required for US addresses')
      : z.string().optional(),
  });
};

function DynamicSchemaForm() {
  const [hasCompany, setHasCompany] = useState(false);
  const [country, setCountry] = useState('');

  const schema = useMemo(
    () => createSchema(hasCompany, country),
    [hasCompany, country]
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        type="checkbox"
        {...register('hasCompany')}
        onChange={(e) => setHasCompany(e.target.checked)}
      />

      <select
        {...register('country')}
        onChange={(e) => setCountry(e.target.value)}
      >
        {/* options */}
      </select>

      {/* Conditional fields */}
    </form>
  );
}
```

**useWatch for Performance**
```tsx
import { useForm, useWatch } from 'react-hook-form';

function PerformantConditionalForm() {
  const { register, control, handleSubmit } = useForm();

  // useWatch only re-renders this component, not the entire form
  const paymentMethod = useWatch({
    control,
    name: 'paymentMethod',
    defaultValue: 'credit_card',
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <select {...register('paymentMethod')}>
        <option value="credit_card">Credit Card</option>
        <option value="paypal">PayPal</option>
        <option value="bank_transfer">Bank Transfer</option>
      </select>

      {paymentMethod === 'credit_card' && <CreditCardFields register={register} />}
      {paymentMethod === 'paypal' && <PayPalFields register={register} />}
      {paymentMethod === 'bank_transfer' && <BankFields register={register} />}
    </form>
  );
}
```

**Unregister Hidden Fields**
```tsx
import { useEffect } from 'react';

function FormWithUnregister() {
  const { register, unregister, watch } = useForm();
  const showExtraField = watch('showExtraField');

  useEffect(() => {
    if (!showExtraField) {
      // Unregister field when hidden to remove from form data
      unregister('extraField');
    }
  }, [showExtraField, unregister]);

  return (
    <form>
      <input type="checkbox" {...register('showExtraField')} />

      {showExtraField && (
        <input {...register('extraField')} />
      )}
    </form>
  );
}
```

### Anti-Pattern

❌ **WRONG: Watching entire form**
```tsx
const formValues = watch(); // Watches ALL fields
// Re-renders on every field change
```

✅ **CORRECT: Watch specific fields**
```tsx
const hasCompany = watch('hasCompany'); // Only watches one field
// Re-renders only when hasCompany changes
```

---

## 10. Auto-Save Drafts

### Problem
Automatically save form progress to prevent data loss.

### Solution
Use debounced auto-save with localStorage or API endpoint.

### Implementation

**Auto-Save to localStorage**
```tsx
import { useForm } from 'react-hook-form';
import { useEffect } from 'react';
import { debounce } from 'lodash-es';

const STORAGE_KEY = 'form-draft';

function AutoSaveForm() {
  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { isDirty },
  } = useForm({
    defaultValues: () => {
      // Load saved draft on mount
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : {};
    },
  });

  // Watch all form values
  const formValues = watch();

  // Debounced save function
  useEffect(() => {
    const saveDraft = debounce(() => {
      if (isDirty) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(formValues));
        console.log('Draft saved');
      }
    }, 1000); // Save after 1 second of inactivity

    saveDraft();

    return () => saveDraft.cancel();
  }, [formValues, isDirty]);

  const onSubmit = async (data: FormData) => {
    try {
      await api.submitForm(data);
      // Clear draft after successful submission
      localStorage.removeItem(STORAGE_KEY);
      toast.success('Form submitted!');
    } catch (error) {
      toast.error('Failed to submit form');
    }
  };

  const clearDraft = () => {
    localStorage.removeItem(STORAGE_KEY);
    reset();
    toast.info('Draft cleared');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Contact Form</h2>
        <button
          type="button"
          onClick={clearDraft}
          className="text-sm text-gray-600 hover:text-gray-800"
        >
          Clear Draft
        </button>
      </div>

      <div>
        <label htmlFor="name">Name</label>
        <input id="name" {...register('name')} />
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email')} />
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea id="message" {...register('message')} rows={4} />
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md"
      >
        Submit
      </button>
    </form>
  );
}
```

**Auto-Save to API with Status Indicator**
```tsx
import { useForm } from 'react-hook-form';
import { useEffect, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { debounce } from 'lodash-es';

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

function AutoSaveToAPI() {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const {
    register,
    watch,
    formState: { isDirty },
  } = useForm();

  const saveMutation = useMutation({
    mutationFn: async (data: FormData) => {
      return await api.saveDraft(data);
    },
    onMutate: () => {
      setSaveStatus('saving');
    },
    onSuccess: () => {
      setSaveStatus('saved');
      setLastSaved(new Date());
      setTimeout(() => setSaveStatus('idle'), 2000);
    },
    onError: () => {
      setSaveStatus('error');
    },
  });

  const formValues = watch();

  useEffect(() => {
    const autoSave = debounce(() => {
      if (isDirty) {
        saveMutation.mutate(formValues);
      }
    }, 2000);

    autoSave();

    return () => autoSave.cancel();
  }, [formValues, isDirty]);

  return (
    <div>
      {/* Save Status Indicator */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {saveStatus === 'saving' && (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span className="text-sm text-gray-600">Saving...</span>
            </>
          )}
          {saveStatus === 'saved' && (
            <>
              <svg
                className="h-4 w-4 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="text-sm text-green-600">
                Saved {lastSaved && `at ${lastSaved.toLocaleTimeString()}`}
              </span>
            </>
          )}
          {saveStatus === 'error' && (
            <>
              <svg
                className="h-4 w-4 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
              <span className="text-sm text-red-600">Failed to save</span>
            </>
          )}
        </div>
      </div>

      <form className="space-y-4">
        {/* Form fields */}
      </form>
    </div>
  );
}
```

### Anti-Pattern

❌ **WRONG: Saving on every keystroke**
```tsx
const formValues = watch();
useEffect(() => {
  api.saveDraft(formValues); // No debounce, floods API
}, [formValues]);
```

✅ **CORRECT: Debounced auto-save**
```tsx
useEffect(() => {
  const saveDraft = debounce(() => {
    api.saveDraft(formValues);
  }, 2000);
  saveDraft();
  return () => saveDraft.cancel();
}, [formValues]);
```

---

## 11. Submit Error Handling

### Problem
Handle form submission errors gracefully with user feedback and retry logic.

### Solution
Use TanStack Query mutations with optimistic updates and error recovery.

### Implementation

**Form Submission with TanStack Query**
```tsx
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

interface FormData {
  title: string;
  content: string;
}

function SubmitErrorHandlingForm() {
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<FormData>();

  const createPostMutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw error;
      }

      return response.json();
    },
    onSuccess: (data) => {
      // Invalidate and refetch queries
      queryClient.invalidateQueries({ queryKey: ['posts'] });

      toast.success('Post created successfully!');
      reset(); // Reset form
    },
    onError: (error: any) => {
      // Handle different error types
      if (error.field) {
        // Field-specific error
        setError(error.field, {
          type: 'manual',
          message: error.message,
        });
      } else if (error.message) {
        // General error
        toast.error(error.message);
      } else {
        // Unknown error
        toast.error('Failed to create post. Please try again.');
      }
    },
  });

  const onSubmit = (data: FormData) => {
    createPostMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          {...register('title', { required: 'Title is required' })}
          className={errors.title ? 'border-red-500' : ''}
        />
        {errors.title && (
          <p className="text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="content">Content</label>
        <textarea
          id="content"
          {...register('content', { required: 'Content is required' })}
          rows={4}
          className={errors.content ? 'border-red-500' : ''}
        />
        {errors.content && (
          <p className="text-sm text-red-600">{errors.content.message}</p>
        )}
      </div>

      {/* Error Message */}
      {createPostMutation.isError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-start">
            <svg
              className="h-5 w-5 text-red-600 mt-0.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Failed to create post
              </h3>
              <p className="mt-1 text-sm text-red-700">
                {createPostMutation.error?.message || 'An unexpected error occurred'}
              </p>
              <button
                type="button"
                onClick={() => createPostMutation.reset()}
                className="mt-2 text-sm font-medium text-red-800 hover:text-red-900"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center space-x-4">
        <button
          type="submit"
          disabled={isSubmitting || createPostMutation.isPending}
          className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
        >
          {createPostMutation.isPending ? 'Creating...' : 'Create Post'}
        </button>

        {/* Retry Button */}
        {createPostMutation.isError && (
          <button
            type="button"
            onClick={() => handleSubmit(onSubmit)()}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Retry
          </button>
        )}
      </div>
    </form>
  );
}
```

**Optimistic Updates Pattern**
```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

function OptimisticUpdateForm() {
  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await api.updatePost(data);
      return response;
    },
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['post', newData.id] });

      // Snapshot the previous value
      const previousPost = queryClient.getQueryData(['post', newData.id]);

      // Optimistically update to the new value
      queryClient.setQueryData(['post', newData.id], newData);

      // Return context with snapshot
      return { previousPost };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousPost) {
        queryClient.setQueryData(['post', variables.id], context.previousPost);
      }
      toast.error('Failed to update post');
    },
    onSuccess: () => {
      toast.success('Post updated!');
    },
    onSettled: (data, error, variables) => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['post', variables.id] });
    },
  });

  const onSubmit = (data: FormData) => {
    updateMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}

      {/* Show optimistic state in UI */}
      {updateMutation.isPending && (
        <div className="fixed bottom-4 right-4 px-4 py-2 bg-blue-600 text-white rounded-md shadow-lg">
          Saving changes...
        </div>
      )}
    </form>
  );
}
```

### Anti-Pattern

❌ **WRONG: Generic error handling**
```tsx
try {
  await api.submit(data);
} catch (error) {
  alert('Error!'); // No context, poor UX
}
```

✅ **CORRECT: Specific error handling**
```tsx
onError: (error) => {
  if (error.field) {
    setError(error.field, { message: error.message });
  } else {
    toast.error(error.message);
  }
}
```

---

## 12. Performance Optimization

### Problem
Forms with many fields cause excessive re-renders and slow performance.

### Solution
Use React Hook Form's uncontrolled approach, `useWatch` for selective subscriptions, and React.memo for components.

### Implementation

**Uncontrolled Components (Default)**
```tsx
// ✅ React Hook Form uses refs, minimal re-renders
function FastForm() {
  const { register, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* No re-renders on input change */}
      <input {...register('name')} />
      <input {...register('email')} />
      <input {...register('phone')} />
      {/* ... 50+ more fields */}
    </form>
  );
}
```

**useWatch for Selective Re-renders**
```tsx
import { useForm, useWatch } from 'react-hook-form';
import { memo } from 'react';

function Form() {
  const { register, control, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('firstName')} />
      <input {...register('lastName')} />
      <input {...register('country')} />

      {/* Only this component re-renders when country changes */}
      <StateField control={control} />
    </form>
  );
}

// Memoized component that only watches specific field
const StateField = memo(({ control }: { control: Control }) => {
  const country = useWatch({
    control,
    name: 'country',
  });

  if (country !== 'US') return null;

  return (
    <div>
      <label>State</label>
      <select {...register('state')}>
        <option value="CA">California</option>
        <option value="NY">New York</option>
      </select>
    </div>
  );
});
```

**Optimizing Field Arrays**
```tsx
import { useFieldArray } from 'react-hook-form';

function OptimizedFieldArray() {
  const { control } = useForm();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  return (
    <div>
      {fields.map((field, index) => (
        // Use field.id as key for optimal re-renders
        <ItemRow key={field.id} index={index} control={control} onRemove={remove} />
      ))}
    </div>
  );
}

// Memoized row component
const ItemRow = memo(({ index, control, onRemove }: Props) => {
  const { register } = useFormContext();

  return (
    <div className="flex gap-2">
      <input {...register(`items.${index}.name`)} />
      <input {...register(`items.${index}.quantity`)} type="number" />
      <button type="button" onClick={() => onRemove(index)}>
        Remove
      </button>
    </div>
  );
});
```

**Debounced Validation**
```tsx
import { useForm } from 'react-hook-form';

function FormWithDebouncedValidation() {
  const { register, handleSubmit } = useForm({
    mode: 'onBlur', // Validate only on blur, not on every keystroke
    reValidateMode: 'onChange', // Re-validate on change after first submit
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
    </form>
  );
}
```

**Lazy Loading Heavy Components**
```tsx
import { lazy, Suspense } from 'react';

// Lazy load rich text editor
const RichTextEditor = lazy(() => import('./RichTextEditor'));

function FormWithLazyComponents() {
  const { register, control } = useForm();

  return (
    <form>
      <input {...register('title')} />

      <Suspense fallback={<div>Loading editor...</div>}>
        <RichTextEditor control={control} name="content" />
      </Suspense>
    </form>
  );
}
```

### Performance Checklist

**✅ Do:**
- Use uncontrolled components (default in RHF)
- Use `useWatch` instead of `watch()` for conditional rendering
- Memoize expensive components with `React.memo`
- Use `mode: 'onBlur'` for validation
- Debounce async validation
- Use `field.id` as key in field arrays

**❌ Don't:**
- Call `watch()` without arguments (watches all fields)
- Use controlled components unless necessary
- Put complex logic in render function
- Validate on every keystroke for large forms
- Use index as key in field arrays

### Anti-Pattern

❌ **WRONG: Watching all fields**
```tsx
const allValues = watch(); // Re-renders on EVERY field change
return (
  <div>
    {/* Uses only one field but watches all */}
    {allValues.country === 'US' && <StateField />}
  </div>
);
```

✅ **CORRECT: Watch specific field**
```tsx
const country = useWatch({ control, name: 'country' });
// Only re-renders when country changes
```

---

## 13. Common Anti-Patterns

### Anti-Pattern 1: Manual State for Every Field

❌ **WRONG:**
```tsx
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [name, setName] = useState('');
const [phone, setPhone] = useState('');
// ... 20 more fields

return (
  <form>
    <input value={email} onChange={(e) => setEmail(e.target.value)} />
    <input value={password} onChange={(e) => setPassword(e.target.value)} />
    {/* Component re-renders on every keystroke */}
  </form>
);
```

✅ **CORRECT:**
```tsx
const { register, handleSubmit } = useForm<FormData>();

return (
  <form onSubmit={handleSubmit(onSubmit)}>
    <input {...register('email')} />
    <input {...register('password')} />
    {/* No re-renders, better performance */}
  </form>
);
```

---

### Anti-Pattern 2: Scattered Validation Logic

❌ **WRONG:**
```tsx
const validateEmail = (email: string) => {
  if (!email) return 'Required';
  if (!email.includes('@')) return 'Invalid';
  // Validation logic scattered across component
};

const validatePassword = (password: string) => {
  if (!password) return 'Required';
  if (password.length < 8) return 'Too short';
  // Hard to maintain, no type inference
};
```

✅ **CORRECT:**
```tsx
const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});
// Single source of truth, automatic TypeScript types
```

---

### Anti-Pattern 3: Not Connecting Error Messages

❌ **WRONG:**
```tsx
<input name="email" />
{errors.email && <p>{errors.email.message}</p>}
// Screen readers can't connect error to input
```

✅ **CORRECT:**
```tsx
<input
  id="email"
  aria-invalid={!!errors.email}
  aria-describedby={errors.email ? 'email-error' : undefined}
/>
{errors.email && (
  <p id="email-error" role="alert">
    {errors.email.message}
  </p>
)}
```

---

### Anti-Pattern 4: No Debouncing for Async Validation

❌ **WRONG:**
```tsx
<input
  onChange={async (e) => {
    const available = await api.checkUsername(e.target.value);
    // API call on EVERY keystroke
  }}
/>
```

✅ **CORRECT:**
```tsx
const checkUsername = useMemo(
  () => debounce(async (username: string) => {
    const available = await api.checkUsername(username);
  }, 500),
  []
);
```

---

### Anti-Pattern 5: Using fetch() for File Upload Progress

❌ **WRONG:**
```tsx
const upload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  await fetch('/upload', {
    method: 'POST',
    body: formData,
  });
  // No way to track upload progress
};
```

✅ **CORRECT:**
```tsx
const upload = (file: File) => {
  const xhr = new XMLHttpRequest();

  xhr.upload.addEventListener('progress', (e) => {
    const progress = (e.loaded / e.total) * 100;
    setUploadProgress(progress);
  });

  xhr.send(formData);
};
```

---

### Anti-Pattern 6: Watching All Fields

❌ **WRONG:**
```tsx
const allValues = watch(); // Subscribes to ALL fields

return (
  <div>
    {allValues.showExtra && <ExtraField />}
    {/* Re-renders on EVERY field change */}
  </div>
);
```

✅ **CORRECT:**
```tsx
const showExtra = useWatch({ control, name: 'showExtra' });
// Only re-renders when showExtra changes
```

---

### Anti-Pattern 7: Not Handling Server Errors

❌ **WRONG:**
```tsx
const onSubmit = async (data: FormData) => {
  try {
    await api.submit(data);
  } catch (error) {
    console.error(error); // User has no feedback
  }
};
```

✅ **CORRECT:**
```tsx
const mutation = useMutation({
  mutationFn: api.submit,
  onError: (error: any) => {
    if (error.field) {
      setError(error.field, { message: error.message });
    } else {
      toast.error(error.message || 'Submission failed');
    }
  },
});
```

---

### Anti-Pattern 8: Missing Loading States

❌ **WRONG:**
```tsx
<button type="submit">Submit</button>
// No indication of submission in progress
```

✅ **CORRECT:**
```tsx
<button
  type="submit"
  disabled={isSubmitting}
  aria-busy={isSubmitting}
>
  {isSubmitting ? 'Submitting...' : 'Submit'}
</button>
```

---

### Anti-Pattern 9: Not Resetting Form After Success

❌ **WRONG:**
```tsx
const onSubmit = async (data: FormData) => {
  await api.submit(data);
  toast.success('Submitted!');
  // Form still has old values
};
```

✅ **CORRECT:**
```tsx
const onSubmit = async (data: FormData) => {
  await api.submit(data);
  reset(); // Clear form
  toast.success('Submitted!');
};
```

---

### Anti-Pattern 10: Manual Array Management

❌ **WRONG:**
```tsx
const [items, setItems] = useState([{ value: '' }]);

const addItem = () => {
  setItems([...items, { value: '' }]);
  // No validation, manual state management
};
```

✅ **CORRECT:**
```tsx
const { fields, append } = useFieldArray({
  control,
  name: 'items',
});

const addItem = () => {
  append({ value: '' });
  // Type-safe, validated, optimized
};
```

---

## Summary

### Key Patterns

1. **React Hook Form + Zod** - Modern, type-safe form handling with schema validation
2. **Uncontrolled Components** - Default in RHF for best performance
3. **useFieldArray** - Optimized dynamic field arrays
4. **useWatch/useFormState** - Selective re-renders for conditional logic
5. **Debounced Async Validation** - Prevent excessive API calls
6. **Accessibility First** - ARIA attributes, keyboard navigation, screen reader support
7. **TanStack Query Integration** - Error handling, optimistic updates, retry logic
8. **Auto-Save with Debounce** - Prevent data loss with localStorage or API
9. **Multi-Step Forms** - State persistence across wizard steps
10. **File Upload with Progress** - react-dropzone + XMLHttpRequest

### Common Mistakes

1. ❌ Using controlled state for every field (use `register` instead)
2. ❌ Scattered validation logic (use Zod schemas)
3. ❌ Missing ARIA attributes for accessibility
4. ❌ No debouncing for async validation
5. ❌ Using `fetch()` for upload progress (use XMLHttpRequest)
6. ❌ Watching all fields (use `useWatch` for specific fields)
7. ❌ Poor error handling (use TanStack Query mutations)
8. ❌ No loading states during submission
9. ❌ Not resetting form after success
10. ❌ Manual array state management (use `useFieldArray`)

### Quick Reference

**Basic Form Setup:**
```tsx
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

**Conditional Fields:**
```tsx
const showField = useWatch({ control, name: 'trigger' });
{showField && <input {...register('conditional')} />}
```

**Field Arrays:**
```tsx
const { fields, append, remove } = useFieldArray({
  control,
  name: 'items',
});
```

**File Upload:**
```tsx
<Controller
  name="file"
  control={control}
  render={({ field }) => (
    <Dropzone onDrop={field.onChange} />
  )}
/>
```

**Async Validation:**
```tsx
const checkUsername = useMemo(
  () => debounce(async (value) => {
    const available = await api.check(value);
    if (!available) setError('username', { message: 'Taken' });
  }, 500),
  []
);
```

**Auto-Save:**
```tsx
useEffect(() => {
  const save = debounce(() => {
    localStorage.setItem('draft', JSON.stringify(formValues));
  }, 1000);
  save();
  return () => save.cancel();
}, [formValues]);
```

---

## Related Skills

- **[api-design.md](./api-design.md)** - REST API patterns for form endpoints
- **[frontend-development.md](./frontend-development.md)** - General React patterns
- **[tanstack-query-patterns.md](./tanstack-query-patterns.md)** - Data fetching and mutations
- **[react-performance-patterns.md](./react-performance-patterns.md)** - Performance optimization
- **[testing-strategy.md](./testing-strategy.md)** - Form testing patterns

---

## Sources

- [React Hook Form Official Docs](https://react-hook-form.com/)
- [Zod Documentation](https://zod.dev/)
- [React Hook Form TypeScript Support](https://react-hook-form.com/ts)
- [Best Practices for React Forms (2025)](https://medium.com/@farzanekazemi8517/best-practices-for-handling-forms-in-react-2025-edition-62572b14452f)
- [React Hook Form vs React 19](https://blog.logrocket.com/react-hook-form-vs-react-19/)
- [Zod TypeScript Validation](https://www.freecodecamp.org/news/react-form-validation-zod-react-hook-form/)
- [Form Schema Validation with Zod](https://refine.dev/blog/zod-typescript/)
- [React Accessibility Docs](https://legacy.reactjs.org/docs/accessibility.html)
- [React Aria Components](https://react-spectrum.adobe.com/react-aria/)
- [Creating Accessible Forms in React](https://dev.to/mitevskasar/creating-accessible-forms-in-react-363e)
- [React Dropzone](https://github.com/react-dropzone/react-dropzone)
- [File Upload Guide](https://medium.com/@dlrnjstjs/the-complete-react-file-upload-guide-from-drag-drop-to-progress-tracking-b2edb40016c2)
- [Multi-Step Forms with React](https://www.ignek.com/blog/building-multi-step-forms-in-react/)
- [TanStack Query Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)
- [Debounce Form Inputs](https://blog.benorloff.co/debounce-form-inputs-with-react-hook-form)
- [Auto-Save with React Hooks](https://www.synthace.com/blog/autosave-with-react-hooks)
