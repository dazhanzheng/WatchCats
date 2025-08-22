; 数据迁移辅助函数

// 安全复制文件
function SafeFileCopy(const Source, Dest: String): Boolean;
var
  ErrorCode: Integer;
begin
  Result := False;
  try
    // 确保目标目录存在
    ForceDirectories(ExtractFilePath(Dest));
    
    // 尝试使用 Windows 命令复制
    if not FileCopy(Source, Dest, False) then
    begin
      // 如果 FileCopy 失败，尝试使用 cmd
      if Exec('cmd.exe', '/C copy /Y "' + Source + '" "' + Dest + '"', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
      begin
        Result := (ErrorCode = 0) and FileExists(Dest);
      end;
    end
    else
    begin
      Result := True;
    end;
  except
    Result := False;
  end;
end;

// 安全复制目录
function SafeDirCopy(const Source, Dest: String): Boolean;
var
  ErrorCode: Integer;
  RobocopyCmd: String;
begin
  Result := False;
  try
    // 确保目标目录存在
    ForceDirectories(Dest);
    
    // 使用 robocopy (Windows 自带，比 xcopy 更可靠)
    // /E: 复制子目录（包括空目录）
    // /NP: 不显示进度
    // /NS /NC /NFL /NDL /NJH /NJS: 静默模式
    RobocopyCmd := '/C robocopy "' + Source + '" "' + Dest + '" /E /NP /NS /NC /NFL /NDL /NJH /NJS';
    
    if Exec('cmd.exe', RobocopyCmd, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
    begin
      // Robocopy 返回代码: 0=没有文件复制, 1=文件复制成功, 2=有额外文件
      // 3=文件复制成功且有额外文件, 4=有不匹配, 8=有错误
      Result := (ErrorCode < 8); // 小于8表示成功
    end;
    
    // 如果 robocopy 不可用，尝试 xcopy
    if not Result then
    begin
      if Exec('cmd.exe', '/C xcopy "' + Source + '\*.*" "' + Dest + '\" /E /Y /I', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
      begin
        Result := (ErrorCode = 0);
      end;
    end;
  except
    Result := False;
  end;
end;

// 改进的数据迁移函数
procedure MigrateOldDataImproved();
var
  OldConfigPath: String;
  NewConfigPath: String;
  BackupPath: String;
  ResultCode: Integer;
  StatusText: String;
  FilesCopied: Integer;
  FailedFiles: String;
  Success: Boolean;
  i: Integer;
  FilesToMigrate: array[0..4] of String;
  CurrentFile: String;
  SourceFile: String;
  DestFile: String;
begin
  // 定义路径
  OldConfigPath := ExpandConstant('{userappdata}\BaalPet');
  NewConfigPath := ExpandConstant('{localappdata}\WatchCats');
  BackupPath := ExpandConstant('{localappdata}\WatchCats_backup');
  
  // 检查旧版本目录是否存在
  if not DirExists(OldConfigPath) then
  begin
    Exit; // 没有旧数据，直接退出
  end;
  
  // 显示迁移状态
  StatusText := '检测到旧版本数据，正在准备迁移...';
  if GetUILanguage <> $0804 then
    StatusText := 'Old version data detected, preparing migration...';
  
  WizardForm.StatusLabel.Caption := StatusText;
  WizardForm.ProgressGauge.Style := npbstMarquee;
  
  // 如果新目录已存在且有文件，先备份
  if DirExists(NewConfigPath) and FileExists(NewConfigPath + '\config.json') then
  begin
    if GetUILanguage = $0804 then
    begin
      if MsgBox('检测到新版本已有配置文件。' + #13#10 + 
                '是否备份现有配置并迁移旧版本数据？' + #13#10 + 
                '备份路径: ' + BackupPath, 
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        // 备份现有数据
        SafeDirCopy(NewConfigPath, BackupPath);
      end
      else
      begin
        WizardForm.ProgressGauge.Style := npbstNormal;
        Exit; // 用户选择不迁移
      end;
    end;
  end;
  
  // 确保新目录存在
  ForceDirectories(NewConfigPath);
  
  // 定义要迁移的文件列表
  FilesToMigrate[0] := 'config.json';
  FilesToMigrate[1] := 'chat_history.json';
  FilesToMigrate[2] := 'schedules.json';
  FilesToMigrate[3] := 'goals.json';
  FilesToMigrate[4] := 'supervision_config.json';
  
  FilesCopied := 0;
  FailedFiles := '';
  
  // 迁移单个文件
  for i := 0 to 4 do
  begin
    CurrentFile := FilesToMigrate[i];
    SourceFile := OldConfigPath + '\' + CurrentFile;
    DestFile := NewConfigPath + '\' + CurrentFile;
    
    if FileExists(SourceFile) then
    begin
      // 如果目标文件不存在，或用户选择覆盖
      if not FileExists(DestFile) then
      begin
        if SafeFileCopy(SourceFile, DestFile) then
        begin
          FilesCopied := FilesCopied + 1;
        end
        else
        begin
          FailedFiles := FailedFiles + CurrentFile + ', ';
        end;
      end;
    end;
  end;
  
  // 迁移 memory 文件夹
  if DirExists(OldConfigPath + '\memory') then
  begin
    StatusText := '正在迁移记忆数据...';
    if GetUILanguage <> $0804 then
      StatusText := 'Migrating memory data...';
    WizardForm.StatusLabel.Caption := StatusText;
    
    if SafeDirCopy(OldConfigPath + '\memory', NewConfigPath + '\memory') then
    begin
      FilesCopied := FilesCopied + 1;
    end
    else
    begin
      FailedFiles := FailedFiles + 'memory folder, ';
    end;
  end;
  
  // 迁移 logs 文件夹（可选）
  if DirExists(OldConfigPath + '\logs') then
  begin
    SafeDirCopy(OldConfigPath + '\logs', NewConfigPath + '\logs');
    // 日志迁移失败不报错
  end;
  
  WizardForm.ProgressGauge.Style := npbstNormal;
  
  // 显示迁移结果
  if FilesCopied > 0 then
  begin
    if FailedFiles <> '' then
    begin
      // 部分成功
      if GetUILanguage = $0804 then
      begin
        MsgBox('数据迁移部分成功！' + #13#10 + 
               '成功迁移: ' + IntToStr(FilesCopied) + ' 个项目' + #13#10 +
               '失败项目: ' + FailedFiles + #13#10 +
               '您可以手动复制失败的文件。' + #13#10 +
               '旧数据位置: ' + OldConfigPath + #13#10 +
               '新数据位置: ' + NewConfigPath,
               mbInformation, MB_OK);
      end;
    end
    else
    begin
      // 完全成功，只提示用户可以手动删除
      if GetUILanguage = $0804 then
      begin
        MsgBox('数据迁移成功！' + #13#10 + 
               '成功迁移 ' + IntToStr(FilesCopied) + ' 个项目。' + #13#10 +
               #13#10 +
               '旧版本数据已保留在：' + #13#10 + 
               OldConfigPath + #13#10 +
               #13#10 +
               '建议：确认新版本正常运行后，您可以手动删除旧数据文件夹。',
               mbInformation, MB_OK);
      end
      else
      begin
        MsgBox('Data migration successful!' + #13#10 + 
               'Successfully migrated ' + IntToStr(FilesCopied) + ' items.' + #13#10 +
               #13#10 +
               'Old data preserved at:' + #13#10 + 
               OldConfigPath + #13#10 +
               #13#10 +
               'Recommendation: After confirming the new version works properly, you can manually delete the old data folder.',
               mbInformation, MB_OK);
      end;
    end;
  end
  else if FailedFiles <> '' then
  begin
    // 完全失败
    if GetUILanguage = $0804 then
    begin
      MsgBox('数据迁移失败！' + #13#10 + 
             '无法复制文件，可能是权限问题。' + #13#10 +
             #13#10 +
             '请手动复制以下文件夹的内容：' + #13#10 +
             '从: ' + OldConfigPath + #13#10 +
             '到: ' + NewConfigPath + #13#10 +
             #13#10 +
             '或者以管理员身份运行安装程序。',
             mbError, MB_OK);
    end;
  end;
end;