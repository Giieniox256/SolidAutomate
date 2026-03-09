import pythoncom
import win32com.client


class SolidWorksService:

    def __init__(self):
        self.sw = None
        self.swModel = None
        self.com_initialized = False

    def initialize(self):
        if not self.com_initialized:
            pythoncom.CoInitialize()
            self.com_initialized = True

    def shutdown(self):
        if self.sw:
            self.sw = None
        if self.com_initialized:
            pythoncom.CoUninitialize()
            self.com_initialized = False

    def connect(self):
        self.initialize()

        if self.sw:
            return True

        try:
            try:
                self.sw = win32com.client.GetActiveObject("SldWorks.Application")
            except:
                self.sw = win32com.client.Dispatch("SldWorks.Application")
            self.sw.Visible = True
            return True
        except Exception as e:
            print(f"Connect error {e}")  # optional error
            return False

    def disconnect(self):
        """Method to disconnect from SldWorks service"""
        self.shutdown()

    def open_part(self, file_path):
        """Method opening part"""
        if not self.sw:
            return False
        arg_type = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 1)
        arg_options = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 1)
        errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        self.sw.OpenDoc6(file_path, arg_type, arg_options, "", errors, warnings)

    def open_drawing(self, file_path):
        """Method opening drawing"""
        arg_type = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 3)
        arg_options = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 1)
        errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        self.sw.OpenDoc6(file_path, arg_type, arg_options, "", errors, warnings)

    def get_active_document(self):
        try:
            self.swModel = self.sw.ActiveDoc
            return self.swModel
        except Exception as e:
            return str(e)

    def clear_active_document(self):
        self.swModel = None

    def save_drawing_to_pdf(self, file_path=None, file_name=None):
        if not self.swModel.GetType == 3:
            return False

        swExportPDFData = self.sw.GetExportFileData(1)
        swModelExt = self.swModel.Extension
        arg2 = win32com.client.VARIANT(pythoncom.VT_BOOL, 0)
        arg3 = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        arg4 = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        arg5 = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

        success = swModelExt.SaveAs(f"{file_path}\\{file_name}.pdf", arg2, arg3, swExportPDFData, arg4, arg5)
        return True if success else False

    def save_part_to_step(self, file_path=None, file_name=None):
        if self.swModel.GetType == 1 or self.swModel.GetType == 2:
            arg3 = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            arg4 = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 2)
            success = self.swModel.SaveAs3(f"{file_path}\\{file_name}.STEP", arg3, arg4)
            return True if success == 0 else False

    def save_dxf_metal_sheet(self, file_path=None, file_name=None):
        thickness = ""
        mat = ""
        try:
            prop_dict = self.get_properties()
        except Exception as e:
            return False
        if not isinstance(prop_dict, dict):
            return False
        if "Grubość" in prop_dict:
            thickness = prop_dict["Grubość"]
        elif "Thickness" in prop_dict:
            thickness = prop_dict["Thickness"]
        if "Material" in prop_dict:
            mat = prop_dict["Material"]
        if self.swModel.GetType != 1:
            return False
        file_name_ = f"{file_path}\\{file_name}_{thickness}mm_{mat}_sheet.DXF"
        success = self.swModel.ExportFlatPatternView(file_name_, 0)
        return True if success else False

    def get_properties(self):
        if self.swModel.GetType != 1:
            return

        active_config = self.swModel.GetActiveConfiguration
        prop_manager = active_config.CustomPropertyManager
        vPropNames = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
        vPropTypes = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
        vPropValues = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
        resolved = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
        linkToProp = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)

        result = prop_manager.GetAll3(vPropNames, vPropTypes, vPropValues, resolved, linkToProp)

        arg_str = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")

        mat_name = self.swModel.GetMaterialPropertyName(arg_str)

        dictionary = dict(zip(vPropNames.value, vPropValues.value))
        dictionary["Material"] = mat_name
        return dictionary

    def close_doc(self, pth):
        self.sw.CloseDoc(pth)
