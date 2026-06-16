class ResponseMessages:
    class GENERAL:
        READ = {"en": "Data retrieved successfully", "ar": "تم جلب البيانات بنجاح"}
        CREATE = {"en": "Data created successfully", "ar": "تم اضافة البيانات بنجاح"}
        UPDATE = {"en": "Data updated successfully", "ar": "تم تعديل البيانات بنجاح"}
        DELETE = {"en": "Data deleted successfully", "ar": "تم حذف البيانات بنجاح"}

    class AUTH:
        LOGIN_SUCCESS = {"en": "Login successful", "ar": "تسجيل دخول ناجح"}
        LOGIN_FAILED = {"en": "Invalid credentials", "ar": "بيانات عير صالحة"}

    class TAGS:
        CREATED = {"en": "Tag created successfully", "ar": "تم إنشاء الوسم بنجاح"}
        DELETED = {"en": "Tag deleted successfully", "ar": "تم حذف الوسم بنجاح"}
        ASSIGN = {"en": "Tag Assigned Successfully", "ar": "تم تعيين الوسم بنجاح"}
        UNASSIGN = {"en": "Tag Unassigned Successfully", "ar": "تم إلغاء تعيين الوسم بنجاح"}
        READ = {"en": "Tag retrieved successfully", "ar": "تم جلب الوسم بنجاح"}

    class CATEGORY:
        CREATED = {"en": "Category created successfully", "ar": "تم إنشاء الفئة بنجاح"}
        DELETED = {"en": "Category deleted successfully", "ar": "تم حذف الفئة بنجاح"}
        ASSIGN = {"en": "Category Assigned Successfully", "ar": "تم تعيين الفئة بنجاح"}
        UNASSIGN = {"en": "Category Unassigned Successfully", "ar": "تم الغاء تعيين الفئة بنجاح"}
        UPDATED = {"en": "Category Updated Successfully", "ar": "تم تعديل الفئة بنجاح"}

    class DATASOURCE:
        READ = {"en": "Datasource retrieved successfully", "ar": "تم جلب مصدر البيانات بنجاح"}
        CREATE = {"en": "Datasource created successfully", "ar": "تم اضافة مصدر البيانات بنجاح"}
        UPDATE = {"en": "Datasource updated successfully", "ar": "تم تعديل مصدر البيانات بنجاح"}
        DELETE = {"en": "Datasource deleted successfully", "ar": "تم حذف مصدر البيانات بنجاح"}

    class DATASET:
        READ = {"en": "Dataset retrieved successfully", "ar": "تم جلب مجموعة البيانات بنجاح"}
        READ_LIST = {"en": "Datasets retrieved successfully", "ar": "تم جلب مجموعات البيانات بنجاح"}
        APPROVE = {"en": "Dataset approved successfully", "ar": "تمت الموافقة على مجموعة البيانات بنجاح"}
        SUBMIT = {"en": "Dataset submitted successfully", "ar": "تم إرسال مجموعة البيانات بنجاح"}
        REJECT = {"en": "Dataset rejected successfully", "ar": "تم رفض مجموعة البيانات بنجاح"}



class Error:
    USER_NOT_FOUND = "User not found"
    INCORRECT_EMAIL_OR_PASSWORD = "Incorrect email or password"
    DATABASE_CONNECTION_FAILUER = "Connection with Datasource is failed..."
