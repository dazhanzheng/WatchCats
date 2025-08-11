; NSIS 安装脚本 - Baal宠物助手
; 需要NSIS 3.0+和简体中文语言文件

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; 基本信息
!define PRODUCT_NAME "Baal宠物助手"
!define PRODUCT_NAME_EN "BaalPetAssistant"
!define PRODUCT_VERSION "0.1.0"
!define PRODUCT_PUBLISHER "Baal Project"
!define PRODUCT_WEB_SITE "https://github.com/yourusername/baal-standalone"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Baal宠物助手.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 设置
!define MUI_ABORTWARNING
!define MUI_ICON "..\baal\resources\cat.ico"
!define MUI_UNICON "..\baal\resources\cat.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP_NOSTRETCH

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 许可协议页面
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
; 安装目录选择页面
!insertmacro MUI_PAGE_DIRECTORY
; 安装组件选择页面
!insertmacro MUI_PAGE_COMPONENTS
; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES
; 安装完成页面
!define MUI_FINISHPAGE_RUN "$INSTDIR\Baal宠物助手.exe"
!define MUI_FINISHPAGE_RUN_TEXT "运行 ${PRODUCT_NAME}"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "查看说明文档"
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_INSTFILES

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

; 安装程序信息
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Output\${PRODUCT_NAME_EN}Setup.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME_EN}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel admin

; 版本信息
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "LegalCopyright" "Copyright © 2025 ${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "FileDescription" "${PRODUCT_NAME} 安装程序"
VIAddVersionKey /LANG=${LANG_SIMPCHINESE} "FileVersion" "${PRODUCT_VERSION}"

; 函数声明
Function .onInit
  ; 检查是否已安装
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  ${If} $R0 != ""
    MessageBox MB_YESNO|MB_ICONQUESTION "检测到已安装 ${PRODUCT_NAME}。$\n$\n是否先卸载旧版本？" IDYES uninst
    Abort
  uninst:
    ExecWait '$R0 /S'
  ${EndIf}
  
  ; 语言选择
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

; 主程序段
Section "主程序" SEC01
  SectionIn RO  ; 必选组件
  
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; 复制主程序
  File "..\dist\Baal宠物助手.exe"
  
  ; 复制资源文件
  SetOutPath "$INSTDIR\baal\resources"
  File /r "..\baal\resources\*"
  
  SetOutPath "$INSTDIR\动作表情拆分"
  File /r "..\动作表情拆分\*"
  
  SetOutPath "$INSTDIR\baal\references"
  File /r "..\baal\references\*"
  
  ; 复制文档
  SetOutPath "$INSTDIR"
  File "..\BUILD_WINDOWS.md"
  Rename "$INSTDIR\BUILD_WINDOWS.md" "$INSTDIR\README.txt"
  
  ; 创建用户数据目录
  CreateDirectory "$APPDATA\${PRODUCT_NAME_EN}"
  CreateDirectory "$APPDATA\${PRODUCT_NAME_EN}\logs"
  CreateDirectory "$APPDATA\${PRODUCT_NAME_EN}\data"
SectionEnd

Section "开始菜单快捷方式" SEC02
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\Baal宠物助手.exe"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\用户手册.lnk" "$INSTDIR\README.txt"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\配置文件夹.lnk" "$APPDATA\${PRODUCT_NAME_EN}"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\卸载.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section "桌面快捷方式" SEC03
  CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\Baal宠物助手.exe"
SectionEnd

Section "开机自动启动" SEC04
  CreateShortcut "$SMSTARTUP\${PRODUCT_NAME}.lnk" "$INSTDIR\Baal宠物助手.exe" "--minimized"
SectionEnd

Section -AdditionalIcons
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  
  ; 写入注册表
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Baal宠物助手.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Baal宠物助手.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  ; 获取安装大小
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
  
  ; 创建URL文件
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
SectionEnd

; 组件描述
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "安装 ${PRODUCT_NAME} 主程序（必需）"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "在开始菜单创建程序快捷方式"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "在桌面创建程序快捷方式"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC04} "Windows启动时自动运行程序"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; 卸载部分
Section Uninstall
  ; 确认卸载
  MessageBox MB_YESNO|MB_ICONQUESTION "确定要完全卸载 ${PRODUCT_NAME} 吗？$\n$\n注意：用户数据将被保留在 $APPDATA\${PRODUCT_NAME_EN}" IDYES +2
  Abort
  
  ; 尝试关闭运行中的程序
  FindWindow $0 "" "${PRODUCT_NAME}"
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONINFORMATION "请先关闭正在运行的 ${PRODUCT_NAME}"
    Abort
  ${EndIf}
  
  ; 删除文件
  Delete "$INSTDIR\Baal宠物助手.exe"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  
  ; 删除目录
  RMDir /r "$INSTDIR\baal"
  RMDir /r "$INSTDIR\动作表情拆分"
  RMDir "$INSTDIR"
  
  ; 删除快捷方式
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\*.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$SMSTARTUP\${PRODUCT_NAME}.lnk"
  
  ; 删除注册表项
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  
  ; 提示用户数据
  MessageBox MB_YESNO|MB_ICONQUESTION "是否删除用户数据和设置？$\n$\n位置：$APPDATA\${PRODUCT_NAME_EN}" IDNO +2
  RMDir /r "$APPDATA\${PRODUCT_NAME_EN}"
  
  SetAutoClose true
SectionEnd

Function un.onInit
  !insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "确定要卸载 ${PRODUCT_NAME} 吗？" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "${PRODUCT_NAME} 已成功从您的计算机中卸载。"
FunctionEnd