unit USBRelayInterface;

interface

uses
  Winapi.Windows;

const
  USB_RELAY_DLL = 'usb_relay_device.dll';

type
  usb_relay_device_type = (
    USB_RELAY_DEVICE_ONE_CHANNEL = 1,
    USB_RELAY_DEVICE_TWO_CHANNEL = 2,
    USB_RELAY_DEVICE_FOUR_CHANNEL = 4,
    USB_RELAY_DEVICE_EIGHT_CHANNEL = 8
  );

  Pusb_relay_device_info = ^usb_relay_device_info;
  usb_relay_device_info = record
    serial_number: PAnsiChar;
    device_path: PAnsiChar;
    device_type: usb_relay_device_type;
    next: Pusb_relay_device_info;
  end;

function usb_relay_init: Integer; cdecl; external USB_RELAY_DLL;
function usb_relay_exit: Integer; cdecl; external USB_RELAY_DLL;
function usb_relay_device_enumerate: Pusb_relay_device_info; cdecl; external USB_RELAY_DLL;
procedure usb_relay_device_free_enumerate(pHead: Pusb_relay_device_info); cdecl; external USB_RELAY_DLL;
function usb_relay_device_open_with_serial_number(const serial_number: PAnsiChar; len: Cardinal): Integer; cdecl; external USB_RELAY_DLL;
function usb_relay_device_open(device_info: Pusb_relay_device_info): Integer; cdecl; external USB_RELAY_DLL;
procedure usb_relay_device_close(hHandle: Integer); cdecl; external USB_RELAY_DLL;
function usb_relay_device_open_one_relay_channel(hHandle: Integer; index: Integer): Integer; cdecl; external USB_RELAY_DLL;
function usb_relay_device_open_all_relay_channel(hHandle: Integer): Integer; cdecl; external USB_RELAY_DLL;
function usb_relay_device_close_one_relay_channel(hHandle: Integer; index: Integer): Integer; cdecl; external USB_RELAY_DLL;
function usb_relay_device_close_all_relay_channel(hHandle: Integer): Integer; cdecl; external USB_RELAY_DLL;
function usb_relay_device_get_status(hHandle: Integer; var status: Cardinal): Integer; cdecl; external USB_RELAY_DLL;

implementation

end.
