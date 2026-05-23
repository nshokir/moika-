program USBRelayController;

uses
  Vcl.Forms,
  MainForm in 'MainForm.pas' {frmUSBRelay},
  USBRelayInterface in 'USBRelayInterface.pas';

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TfrmUSBRelay, frmUSBRelay);
  Application.Run;
end.
