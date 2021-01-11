description = [[ development
]]


author = "hdm"
-- minor tweaks and bugfix by krw
license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
categories = {"discovery", "safe"}

local nmap   = require "nmap"
local comm   = require "comm"
local stdnse = require "stdnse"
local strbuf = require "strbuf"
local nsedebug = require "nsedebug"

---
-- Script is executed for any TCP port.
portrule = function( host, port )
  return port.protocol == "tcp"
end

---
-- Grabs a banner and outputs it nicely formatted.
action = function( host, port )
  local out = grab_banner(host, port, "\187\187\001\000\000\000\001")
  if out == "" then
    -- try a big-endian query
    out = grab_banner(host, port, "\187\187\000\001\000\000\001")
  end
  return output( out )
end

---
-- Returns a number of milliseconds for use as a socket timeout value (defaults to 5 seconds).
--
-- @return Number of milliseconds.
function get_timeout()
  return 5000
end


---
-- Connects to the target on the given port and returns any data issued by a listening service.
-- @param host  Host Table.
-- @param port  Port Table.
-- @return      Socket descriptor and initial banner
function grab_banner(host, port, query)

  local st, buff, banner
  local proto  = "tcp"
  local socket = nmap.new_socket()  
  socket:set_timeout(get_timeout())
  banner = ""
  proto = "tcp"
  st = socket:connect(host, port, proto)
  if not st then
    socket:close()
    return nil
  end
  socket:send(query) 
-- Big endian version
-- socket:send("\187\187\000\001\000\000\001")
-- socket:send("\xbb\xbb\x01\x00\x00\x00\x01")    
  st,banner = socket:receive()
  return banner
end

---
-- Formats the banner for printing to the port script result.
--
-- Non-printable characters are hex encoded and the banner is
-- then truncated to fit into the number of lines of output desired.
-- @param out  String banner issued by a listening service.
-- @return     String formatted for output.
-- Ripped from banner.nse with line wrap disabled (corrupts output)
function output( out )

  if type(out) ~= "string" or out == "" then return nil end

  local filename = SCRIPT_NAME
  local line_len = 75    -- The character width of command/shell prompt window.
  local fline_offset = 5 -- number of chars excluding script id not available to the script on the first line

  -- number of chars available on the first line of output
  -- we'll skip the first line of output if the filename is looong
  local fline_len
  if filename:len() < (line_len-fline_offset) then
    fline_len = line_len -1 -filename:len() -fline_offset
  else
    fline_len = 0
  end

  -- number of chars allowed on subsequent lines
  local sline_len = line_len -1 -(fline_offset-2)

  -- replace non-printable ascii chars - no need to do the whole string
  out = replace_nonprint(out, (out:len() * 3) + 1) -- 1 extra char so we can truncate below.

  -- break into lines - this will look awful if line_len is more than the actual space available on a line...
  local ptr = fline_len
  local t = {}
  t[#t+1] = out

  return table.concat(t,"\n")

end



---
-- Replaces characters with ASCII values outside of the range of standard printable
-- characters (decimal 32 to 126 inclusive) with hex encoded equivalents.
--
-- The second parameter dictates the number of characters to return, however, if the
-- last character before the number is reached is one that needs replacing then up to
-- three characters more than this number may be returned.
-- If the second parameter is nil, no limit is applied to the number of characters
-- that may be returned.
-- @param s    String on which to perform substitutions.
-- @param len  Number of characters to return.
-- @return     String.
-- Pulled from banner.nse and mangled to escape \r\t\n separately
function replace_nonprint( s, len )

  local t = {}
  local count = 0

  for c in s:gmatch(".") do
    if c:byte() == 9 then
      t[#t+1] = ("\\%s"):format("t")
      count = count+3
    elseif c:byte() == 10 then
      t[#t+1] = ("\\%s"):format("n")
      count = count+3     
    elseif c:byte() == 13 then
      t[#t+1] = ("\\%s"):format("r")
      count = count+3            
    elseif c:byte() < 32 or c:byte() > 126 then
      t[#t+1] = ("\\x%s"):format( ("0%s"):format( ( (stdnse.tohex( c:byte() )):upper() ) ):sub(-2,-1) ) -- capiche
      count = count+4
    else
      t[#t+1] = c
      count = count+1
    end
    if type(len) == "number" and count >= len then break end
  end

  return table.concat(t)

end
