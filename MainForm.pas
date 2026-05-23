unit MainForm;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls, Vcl.ExtCtrls,
  USBRelayInterface;

type
  TfrmUSBRelay = class(TForm)
    Panel1: TPanel;
    btnFindDevice: TButton;
    cbDevices: TComboBox;
    btnOpenDevice: TButton;
    btnCloseDevice: TButton;
    Panel2: TPanel;
    Memo1: TMemo;
    Panel3: TPanel;
    btnChannel1On: TButton;
    btnChannel1Off: TButton;
    btnChannel2On: TButton;
    btnChannel2Off: TButton;
    btnChannel3On: TButton;
    btnChannel3Off: TButton;
    btnChannel4On: TButton;
    btnChannel4Off: TButton;
    btnChannel5On: TButton;
    btnChannel5Off: TButton;
    btnChannel6On: TButton;
    btnChannel6Off: TButton;
    btnChannel7On: TButton;
    btnChannel7Off: TButton;
    btnChannel8On: TButton;
    btnChannel8Off: TButton;
    btnGetStatus: TButton;
    btnOpenAll: TButton;
    btnCloseAll: TButton;
    Label1: TLabel;
    Label2: TLabel;
    lblStatus: TLabel;
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure btnFindDeviceClick(Sender: TObject);
    procedure btnOpenDeviceClick(Sender: TObject);
    procedure btnCloseDeviceClick(Sender: TObject);
    procedure btnChannel1OnClick(Sender: TObject);
    procedure btnChannel1OffClick(Sender: TObject);
    procedure btnChannel2OnClick(Sender: TObject);
    procedure btnChannel2OffClick(Sender: TObject);
    procedure btnChannel3OnClick(Sender: TObject);
    procedure btnChannel3OffClick(Sender: TObject);
    procedure btnChannel4OnClick(Sender: TObject);
    procedure btnChannel4OffClick(Sender: TObject);
    procedure btnChannel5OnClick(Sender: TObject);
    procedure btnChannel5OffClick(Sender: TObject);
    procedure btnChannel6OnClick(Sender: TObject);
    procedure btnChannel6OffClick(Sender: TObject);
    procedure btnChannel7OnClick(Sender: TObject);
    procedure btnChannel7OffClick(Sender: TObject);
    procedure btnChannel8OnClick(Sender: TObject);
    procedure btnChannel8OffClick(Sender: TObject);
    procedure btnGetStatusClick(Sender: TObject);
    procedure btnOpenAllClick(Sender: TObject);
    procedure btnCloseAllClick(Sender: TObject);
  private
    FDeviceHandle: Integer;
    FDeviceOpened: Boolean;
    procedure Log(const Msg: string);
    procedure SetChannelState(Channel: Integer; State: Boolean);
  public
  end;

var
  frmUSBRelay: TfrmUSBRelay;

implementation

{$R *.dfm}

procedure TfrmUSBRelay.FormCreate(Sender: TObject);
begin
  FDeviceHandle := -1;
  FDeviceOpened := False;
  lblStatus.Caption := 'Status: Not connected';
  
  if usb_relay_init <> 0 then
  begin
    Log('ERROR: Failed to initialize USB Relay library');
  end
  else
  begin
    Log('USB Relay library initialized successfully');
  end;
end;

procedure TfrmUSBRelay.FormDestroy(Sender: TObject);
begin
  if FDeviceOpened then
    usb_relay_device_close(FDeviceHandle);
  usb_relay_exit;
end;

procedure TfrmUSBRelay.Log(const Msg: string);
begin
  Memo1.Lines.Add('[' + FormatDateTime('hh:mm:ss', Now) + '] ' + Msg);
  Memo1.Lines.EndUpdate;
end;

procedure TfrmUSBRelay.btnFindDeviceClick(Sender: TObject);
var
  pDeviceInfo: Pusb_relay_device_info;
  pCurrent: Pusb_relay_device_info;
  DeviceCount: Integer;
begin
  cbDevices.Clear;
  DeviceCount := 0;
  
  pDeviceInfo := usb_relay_device_enumerate;
  
  if pDeviceInfo = nil then
  begin
    Log('No USB Relay devices found');
    Exit;
  end;
  
  pCurrent := pDeviceInfo;
  while pCurrent <> nil do
  begin
    cbDevices.Items.Add(string(pCurrent^.serial_number));
    Log('Found device: ' + string(pCurrent^.serial_number) + 
        ' (Type: ' + IntToStr(Integer(pCurrent^.device_type)) + ' channels)');
    Inc(DeviceCount);
    pCurrent := pCurrent^.next;
  end;
  
  usb_relay_device_free_enumerate(pDeviceInfo);
  Log('Total devices found: ' + IntToStr(DeviceCount));
  
  if DeviceCount > 0 then
    cbDevices.ItemIndex := 0;
end;

procedure TfrmUSBRelay.btnOpenDeviceClick(Sender: TObject);
var
  SerialNumber: AnsiString;
  Result: Integer;
begin
  if cbDevices.ItemIndex < 0 then
  begin
    Log('ERROR: No device selected');
    Exit;
  end;
  
  if FDeviceOpened then
    usb_relay_device_close(FDeviceHandle);
  
  SerialNumber := AnsiString(cbDevices.Text);
  Result := usb_relay_device_open_with_serial_number(PAnsiChar(SerialNumber), Length(SerialNumber));
  
  if Result > 0 then
  begin
    FDeviceHandle := Result;
    FDeviceOpened := True;
    Log('Device opened successfully. Handle: ' + IntToStr(FDeviceHandle));
    lblStatus.Caption := 'Status: Connected - ' + cbDevices.Text;
    btnFindDevice.Enabled := False;
    cbDevices.Enabled := False;
    btnOpenDevice.Enabled := False;
    btnCloseDevice.Enabled := True;
  end
  else
  begin
    Log('ERROR: Failed to open device');
  end;
end;

procedure TfrmUSBRelay.btnCloseDeviceClick(Sender: TObject);
begin
  if FDeviceOpened then
  begin
    usb_relay_device_close(FDeviceHandle);
    FDeviceOpened := False;
    Log('Device closed');
    lblStatus.Caption := 'Status: Not connected';
    btnFindDevice.Enabled := True;
    cbDevices.Enabled := True;
    btnOpenDevice.Enabled := True;
    btnCloseDevice.Enabled := False;
  end;
end;

procedure TfrmUSBRelay.SetChannelState(Channel: Integer; State: Boolean);
var
  Result: Integer;
begin
  if not FDeviceOpened then
  begin
    Log('ERROR: Device not opened');
    Exit;
  end;
  
  if State then
    Result := usb_relay_device_open_one_relay_channel(FDeviceHandle, Channel)
  else
    Result := usb_relay_device_close_one_relay_channel(FDeviceHandle, Channel);
  
  if Result = 0 then
  begin
    Log('Channel ' + IntToStr(Channel) + ' turned ' + IfThen(State, 'ON', 'OFF'));
  end
  else if Result = 1 then
  begin
    Log('ERROR: Failed to control channel ' + IntToStr(Channel));
  end
  else if Result = 2 then
  begin
    Log('ERROR: Channel ' + IntToStr(Channel) + ' does not exist on this device');
  end;
end;

procedure TfrmUSBRelay.btnChannel1OnClick(Sender: TObject);
begin
  SetChannelState(1, True);
end;

procedure TfrmUSBRelay.btnChannel1OffClick(Sender: TObject);
begin
  SetChannelState(1, False);
end;

procedure TfrmUSBRelay.btnChannel2OnClick(Sender: TObject);
begin
  SetChannelState(2, True);
end;

procedure TfrmUSBRelay.btnChannel2OffClick(Sender: TObject);
begin
  SetChannelState(2, False);
end;

procedure TfrmUSBRelay.btnChannel3OnClick(Sender: TObject);
begin
  SetChannelState(3, True);
end;

procedure TfrmUSBRelay.btnChannel3OffClick(Sender: TObject);
begin
  SetChannelState(3, False);
end;

procedure TfrmUSBRelay.btnChannel4OnClick(Sender: TObject);
begin
  SetChannelState(4, True);
end;

procedure TfrmUSBRelay.btnChannel4OffClick(Sender: TObject);
begin
  SetChannelState(4, False);
end;

procedure TfrmUSBRelay.btnChannel5OnClick(Sender: TObject);
begin
  SetChannelState(5, True);
end;

procedure TfrmUSBRelay.btnChannel5OffClick(Sender: TObject);
begin
  SetChannelState(5, False);
end;

procedure TfrmUSBRelay.btnChannel6OnClick(Sender: TObject);
begin
  SetChannelState(6, True);
end;

procedure TfrmUSBRelay.btnChannel6OffClick(Sender: TObject);
begin
  SetChannelState(6, False);
end;

procedure TfrmUSBRelay.btnChannel7OnClick(Sender: TObject);
begin
  SetChannelState(7, True);
end;

procedure TfrmUSBRelay.btnChannel7OffClick(Sender: TObject);
begin
  SetChannelState(7, False);
end;

procedure TfrmUSBRelay.btnChannel8OnClick(Sender: TObject);
begin
  SetChannelState(8, True);
end;

procedure TfrmUSBRelay.btnChannel8OffClick(Sender: TObject);
begin
  SetChannelState(8, False);
end;

procedure TfrmUSBRelay.btnGetStatusClick(Sender: TObject);
var
  Status: Cardinal;
  Result: Integer;
  i: Integer;
begin
  if not FDeviceOpened then
  begin
    Log('ERROR: Device not opened');
    Exit;
  end;
  
  Result := usb_relay_device_get_status(FDeviceHandle, Status);
  
  if Result = 0 then
  begin
    Log('Device Status: ' + IntToHex(Status, 8));
    for i := 1 to 8 do
    begin
      if (Status and (1 shl (i - 1))) <> 0 then
        Log('  Channel ' + IntToStr(i) + ': ON')
      else
        Log('  Channel ' + IntToStr(i) + ': OFF');
    end;
  end
  else
  begin
    Log('ERROR: Failed to get device status');
  end;
end;

procedure TfrmUSBRelay.btnOpenAllClick(Sender: TObject);
begin
  if not FDeviceOpened then
  begin
    Log('ERROR: Device not opened');
    Exit;
  end;
  
  if usb_relay_device_open_all_relay_channel(FDeviceHandle) = 0 then
    Log('All channels opened')
  else
    Log('ERROR: Failed to open all channels');
end;

procedure TfrmUSBRelay.btnCloseAllClick(Sender: TObject);
begin
  if not FDeviceOpened then
  begin
    Log('ERROR: Device not opened');
    Exit;
  end;
  
  if usb_relay_device_close_all_relay_channel(FDeviceHandle) = 0 then
    Log('All channels closed')
  else
    Log('ERROR: Failed to close all channels');
end;

end.
