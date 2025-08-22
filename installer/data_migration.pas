// 数据迁移辅助函数
// 这个文件包含改进的数据迁移逻辑

// 安全复制文件的函数
function SafeCopyFile(const SourceFile, DestFile: String): Boolean;
var
  ErrorCode: Integer;
begin
  Result := False;
  
  try
    // 确保目标目录存在
    ForceDirectories(ExtractFilePath(DestFile));
    
    // 先尝试 FileCopy
    Result := FileCopy(SourceFile, DestFile, False);
    
    // 如果失败，尝试使用 Windows 命令
    if not Result then
    begin
      if Exec('cmd.exe', '/C copy /Y "' + SourceFile + '" "' + DestFile + '"', 
              '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
      begin
        Result := (ErrorCode = 0) and FileExists(DestFile);
      end;
    end;
  except
    Result := False;
  end;
end;

// 改进的数据迁移函数
procedure MigrateOldDataSafe();
var
  OldConfigPath: String;
  NewConfigPath: String;
  OldMemoryPath: String;
  NewMemoryPath: String;
  ResultCode: Integer;
  StatusText: String;
  FilesCopied: Integer;
  FailedFiles: String;
  MsgText: String;
  LineBreak: String;
begin
  // 定义换行符
  LineBreak := Chr(13) + Chr(10);
  
  // 定义旧版本路径 (BaalPet in Roaming)
  OldConfigPath := ExpandConstant('{userappdata}\BaalPet');
  // 定义新版本路径 (WatchCats in Local)  
  NewConfigPath := ExpandConstant('{localappdata}\WatchCats');
  
  // 记录到日志
  Log('Migration: Old path = ' + OldConfigPath);
  Log('Migration: New path = ' + NewConfigPath);
  
  // 检查旧版本目录是否存在
  if not DirExists(OldConfigPath) then
  begin
    Log('Migration: Old directory not found, skipping migration');
    Exit;
  end;
  
  StatusText := '检测到旧版本数据，正在迁移...';
  if GetUILanguage <> $0804 then
    StatusText := 'Old version data detected, migrating...';
    
  WizardForm.StatusLabel.Caption := StatusText;
  WizardForm.ProgressGauge.Style := npbstMarquee;
  
  // 确保新目录存在
  if not ForceDirectories(NewConfigPath) then
  begin
    Log('Migration: Failed to create new directory');
    MsgText := '无法创建目录: ' + NewConfigPath + LineBreak +
               '请检查权限或手动创建目录后重试。';
    if GetUILanguage <> $0804 then
      MsgText := 'Cannot create directory: ' + NewConfigPath + LineBreak +
                 'Please check permissions or create directory manually.';
    MsgBox(MsgText, mbError, MB_OK);
    Exit;
  end;
  
  FilesCopied := 0;
  FailedFiles := '';
  
  // 迁移 config.json
  if FileExists(OldConfigPath + '\config.json') then
  begin
    Log('Migration: Found config.json');
    if not FileExists(NewConfigPath + '\config.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\config.json', NewConfigPath + '\config.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied config.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'config.json, ';
        Log('Migration: Failed to copy config.json');
      end;
    end
    else
    begin
      Log('Migration: config.json already exists in new location');
    end;
  end;
  
  // 迁移 chat_history.json
  if FileExists(OldConfigPath + '\chat_history.json') then
  begin
    Log('Migration: Found chat_history.json');
    if not FileExists(NewConfigPath + '\chat_history.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\chat_history.json', NewConfigPath + '\chat_history.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied chat_history.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'chat_history.json, ';
        Log('Migration: Failed to copy chat_history.json');
      end;
    end;
  end;
  
  // 迁移 schedules.json
  if FileExists(OldConfigPath + '\schedules.json') then
  begin
    if not FileExists(NewConfigPath + '\schedules.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\schedules.json', NewConfigPath + '\schedules.json') then
      begin
        FilesCopied := FilesCopied + 1;
      end
      else
      begin
        FailedFiles := FailedFiles + 'schedules.json, ';
      end;
    end;
  end;
  
  // 迁移 goals.json
  if FileExists(OldConfigPath + '\goals.json') then
  begin
    if not FileExists(NewConfigPath + '\goals.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\goals.json', NewConfigPath + '\goals.json') then
      begin
        FilesCopied := FilesCopied + 1;
      end
      else
      begin
        FailedFiles := FailedFiles + 'goals.json, ';
      end;
    end;
  end;
  
  // 迁移 memory 文件夹
  OldMemoryPath := OldConfigPath + '\memory';
  NewMemoryPath := NewConfigPath + '\memory';
  
  if DirExists(OldMemoryPath) then
  begin
    Log('Migration: Found memory folder');
    if not DirExists(NewMemoryPath) then
    begin
      ForceDirectories(NewMemoryPath);
      // 使用 xcopy 复制整个文件夹
      if Exec('xcopy.exe', '"' + OldMemoryPath + '\*.*" "' + NewMemoryPath + '\" /E /Y /I', 
              '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      begin
        if ResultCode = 0 then
        begin
          FilesCopied := FilesCopied + 1;
          Log('Migration: Successfully copied memory folder');
        end
        else
        begin
          FailedFiles := FailedFiles + 'memory folder, ';
          Log('Migration: Failed to copy memory folder, error code: ' + IntToStr(ResultCode));
        end;
      end;
    end;
  end;
  
  WizardForm.ProgressGauge.Style := npbstNormal;
  
  // 显示结果
  if FilesCopied > 0 then
  begin
    if FailedFiles <> '' then
    begin
      // 部分成功
      MsgText := '数据迁移部分成功！' + LineBreak + 
                 '成功迁移: ' + IntToStr(FilesCopied) + ' 个项目' + LineBreak +
                 '失败项目: ' + FailedFiles + LineBreak + LineBreak +
                 '请手动复制失败的文件：' + LineBreak +
                 '从: ' + OldConfigPath + LineBreak +
                 '到: ' + NewConfigPath;
      if GetUILanguage <> $0804 then
        MsgText := 'Partial migration success!' + LineBreak +
                   'Migrated: ' + IntToStr(FilesCopied) + ' items' + LineBreak +
                   'Failed: ' + FailedFiles + LineBreak + LineBreak +
                   'Please manually copy failed files:' + LineBreak +
                   'From: ' + OldConfigPath + LineBreak +
                   'To: ' + NewConfigPath;
      MsgBox(MsgText, mbInformation, MB_OK);
    end
    else
    begin
      // 完全成功
      MsgText := '数据迁移成功！' + LineBreak + 
                 '成功迁移 ' + IntToStr(FilesCopied) + ' 个项目。' + LineBreak + LineBreak +
                 '旧版本数据保留在：' + LineBreak + 
                 OldConfigPath + LineBreak + LineBreak +
                 '建议：确认新版本正常运行后，您可以手动删除旧数据文件夹。';
      if GetUILanguage <> $0804 then
        MsgText := 'Migration successful!' + LineBreak +
                   'Migrated ' + IntToStr(FilesCopied) + ' items.' + LineBreak + LineBreak +
                   'Old data preserved at:' + LineBreak +
                   OldConfigPath + LineBreak + LineBreak +
                   'Recommendation: You can manually delete the old folder after confirming everything works.';
      MsgBox(MsgText, mbInformation, MB_OK);
    end;
  end
  else if FailedFiles <> '' then
  begin
    // 完全失败
    MsgText := '数据迁移失败！' + LineBreak + LineBreak +
               '可能的原因：' + LineBreak +
               '1. 权限不足 - 请以管理员身份运行安装程序' + LineBreak +
               '2. 文件被占用 - 请关闭所有相关程序' + LineBreak + LineBreak +
               '请手动复制文件夹：' + LineBreak +
               '从: ' + OldConfigPath + LineBreak +
               '到: ' + NewConfigPath;
    if GetUILanguage <> $0804 then
      MsgText := 'Migration failed!' + LineBreak + LineBreak +
                 'Possible reasons:' + LineBreak +
                 '1. Insufficient permissions - Run installer as administrator' + LineBreak +
                 '2. Files in use - Close all related programs' + LineBreak + LineBreak +
                 'Please manually copy folder:' + LineBreak +
                 'From: ' + OldConfigPath + LineBreak +
                 'To: ' + NewConfigPath;
    MsgBox(MsgText, mbError, MB_OK);
  end;
  
  Log('Migration: Completed with ' + IntToStr(FilesCopied) + ' files copied');
end;