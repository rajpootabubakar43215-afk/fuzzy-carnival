import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Server, BarChart3, Users, Lock, Unlock, ChevronDown, Copy, MapPin, Network, Link as LinkIcon, Trophy, Signal, Map as MapIcon, Gamepad2, User as UserIcon, MessageCircle } from "lucide-react";
import { fetchMasterlist, type CodServer } from "@/lib/codApi";
import { COD_VERSIONS, DEFAULT_VERSION, GAME_TITLE, type CodVersion } from "@/lib/codVersions";
import { CodText } from "@/components/CodText";
import { stripCodCodes } from "@/lib/codColor";
import { getMapImage } from "@/lib/mapImages";
import { detectLinks } from "@/lib/serverLinks";
import { Switch } from "@/components/ui/switch";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

const Index = () => {
  const [version, setVersion] = useState<CodVersion>(DEFAULT_VERSION);
  const [search, setSearch] = useState("");
  const [hidePassword, setHidePassword] = useState(false);
  const [hideEmpty, setHideEmpty] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["masterlist", version.game, version.version],
    queryFn: () => fetchMasterlist(version.game, version.version),
    refetchInterval: 2000,
    refetchIntervalInBackground: true,
  });

  const servers = data?.servers ?? [];

  const filtered = useMemo(() => {
    let s = servers;
    if (hidePassword) s = s.filter((x) => !x.pswrd);
    if (hideEmpty) s = s.filter((x) => x.clients > 0);
    if (search.trim()) {
      const q = search.toLowerCase();
      s = s.filter((x) => {
        const name = stripCodCodes(x.sv_hostname).toLowerCase();
        return (
          name.includes(q) ||
          x.g_gametype?.toLowerCase().includes(q) ||
          x.mapname?.toLowerCase().includes(q) ||
          x.playerinfo?.some((p) => stripCodCodes(p.name).toLowerCase().includes(q))
        );
      });
    }
    return [...s].sort((a, b) => b.clients - a.clients);
  }, [servers, search, hidePassword, hideEmpty]);

  const totalServers = servers.length;
  const activeServers = servers.filter((s) => s.clients > 0).length;
  const activePlayers = servers.reduce((sum, s) => sum + (s.clients || 0), 0);

  const copyConnect = (s: CodServer) => {
    navigator.clipboard.writeText(`/connect ${s.ip}:${s.port}`);
    toast.success("Connect string copied", { description: `${s.ip}:${s.port}` });
  };

  return (
    <main className="min-h-screen px-4 md:px-8 py-6 md:py-10 max-w-[1400px] mx-auto">
      <h1 className="sr-only">United Offensive — Call of Duty Master Server Browser</h1>

      {/* HEADER PANEL */}
      <section className="panel panel-corner panel-glow p-6 md:p-8 mb-6">
        <div className="absolute -top-px left-8 right-8 scanline" />
        <div className="grid lg:grid-cols-[1fr_auto] gap-6 items-start">
          <div className="space-y-3">
            <div className="label-chip">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full rounded-full bg-cyan opacity-75 animate-ping" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan" />
              </span>
              <span className="text-cyan">SYSTEM // ONLINE</span>
            </div>
            <h2 className="font-display text-3xl md:text-5xl font-black tracking-wider text-glow">
              {GAME_TITLE[version.game] ?? "CALL OF DUTY"}
            </h2>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md border border-cyan/40 bg-cyan/5">
              <span className="text-[10px] font-bold tracking-widest text-cyan px-1.5 py-0.5 rounded bg-cyan/10 border border-cyan/40">LIVE</span>
              <span className="font-mono-tech text-cyan text-sm">PATCH {version.version}</span>
            </div>
          </div>

          {/* Search + Version + Toggles */}
          <div className="w-full lg:w-[640px] space-y-3">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search servers, gametypes, maps, or players..."
                  className="w-full bg-panel-2/80 border border-border/70 rounded-lg pl-10 pr-4 py-3 text-sm placeholder:text-muted-foreground/70 focus:outline-none focus:border-cyan/60 focus:ring-1 focus:ring-cyan/40 transition"
                />
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger className="min-w-[140px] flex items-center justify-between gap-2 bg-panel-2/80 border border-cyan/50 rounded-lg px-4 py-3 text-sm font-mono-tech text-cyan hover:border-cyan transition">
                  {version.label}
                  <ChevronDown className="w-4 h-4" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-[220px] bg-panel border-border/70">
                  {COD_VERSIONS.map((g, gi) => (
                    <div key={g.group}>
                      {gi > 0 && <DropdownMenuSeparator />}
                      <DropdownMenuLabel className="text-[10px] tracking-[0.2em] text-muted-foreground uppercase">
                        {g.group}
                      </DropdownMenuLabel>
                      {g.versions.map((v) => {
                        const active = v.game === version.game && v.version === version.version;
                        return (
                          <DropdownMenuItem
                            key={`${v.game}-${v.version}`}
                            onClick={() => { setVersion(v); setExpandedId(null); }}
                            className={`font-mono-tech ${active ? "bg-cyan/20 text-cyan focus:bg-cyan/30" : ""}`}
                          >
                            {v.label}
                          </DropdownMenuItem>
                        );
                      })}
                    </div>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <div className="flex gap-3">
              <div className="flex-1 flex items-center justify-between bg-panel-2/80 border border-border/70 rounded-lg px-4 py-2.5">
                <div className="flex items-center gap-2 text-xs tracking-[0.2em] uppercase text-muted-foreground">
                  <Lock className="w-3.5 h-3.5 text-neon-purple" />
                  Hide Password
                </div>
                <Switch checked={hidePassword} onCheckedChange={setHidePassword} />
              </div>
              <div className="flex-1 flex items-center justify-between bg-panel-2/80 border border-border/70 rounded-lg px-4 py-2.5">
                <div className="flex items-center gap-2 text-xs tracking-[0.2em] uppercase text-muted-foreground">
                  <Users className="w-3.5 h-3.5 text-neon-purple" />
                  Hide Empty
                </div>
                <Switch checked={hideEmpty} onCheckedChange={setHideEmpty} />
              </div>
            </div>
          </div>
        </div>
        <div className="absolute -bottom-px left-8 right-8 scanline" />
      </section>

      {/* STATS */}
      <section className="grid md:grid-cols-3 gap-4 mb-6">
        <StatCard icon={<Server className="w-5 h-5 text-cyan icon-pulse" />} label="Total Servers" value={totalServers} loading={isLoading} />
        <StatCard icon={<BarChart3 className="w-5 h-5 text-cyan icon-pulse" />} label="Active Servers" value={activeServers} loading={isLoading} />
        <StatCard icon={<Users className="w-5 h-5 text-cyan icon-pulse" />} label="Active Players" value={activePlayers} loading={isLoading} />
      </section>

      {/* SERVER TABLE */}
      <section className="panel overflow-hidden">
        <div className="grid grid-cols-[44px_1fr_90px_220px_110px_60px] md:grid-cols-[44px_1fr_120px_260px_140px_70px] items-center px-4 py-3 bg-panel-2/80 border-b border-border/70 text-xs tracking-[0.2em] uppercase text-muted-foreground">
          <div />
          <div className="flex items-center gap-2"><Server className="w-3.5 h-3.5 text-neon-blue icon-glow" /> Server Name</div>
          <div className="flex items-center gap-2"><Gamepad2 className="w-3.5 h-3.5 text-neon-purple icon-glow" /> Type</div>
          <div className="flex items-center gap-2"><MapIcon className="w-3.5 h-3.5 text-neon-green icon-glow" /> Map</div>
          <div className="flex items-center gap-2"><Users className="w-3.5 h-3.5 text-cyan icon-glow" /> Players</div>
          <div className="flex items-center gap-2"><Lock className="w-3.5 h-3.5 text-neon-red icon-glow" /> PW</div>
        </div>

        {isLoading && (
          <div className="p-8 text-center text-muted-foreground font-mono-tech text-sm">
            <span className="animate-pulse">// Fetching masterlist...</span>
          </div>
        )}
        {isError && (
          <div className="p-8 text-center text-neon-red font-mono-tech text-sm">// Failed to load servers</div>
        )}

        {!isLoading && filtered.length === 0 && (
          <div className="p-8 text-center text-muted-foreground font-mono-tech text-sm">// No servers match your filters</div>
        )}

        <div className="divide-y divide-border/40">
          {filtered.map((s) => {
            const expanded = expandedId === s.id;
            return (
              <div key={s.id}>
                <button
                  onClick={() => setExpandedId(expanded ? null : s.id)}
                  className="w-full grid grid-cols-[44px_1fr_90px_220px_110px_60px] md:grid-cols-[44px_1fr_120px_260px_140px_70px] items-center px-4 py-3 row-hover text-left"
                >
                  <div className="flex items-center justify-center">
                    <CountryFlag iso={s.country_isocode} title={s.country_name} />
                  </div>
                  <div className="font-mono-tech text-sm truncate">
                    <CodText text={s.sv_hostname || "Unnamed"} />
                  </div>
                  <div className="font-mono-tech text-sm text-muted-foreground lowercase">{s.g_gametype || "-"}</div>
                  <div className="font-mono-tech text-sm text-muted-foreground truncate">{s.mapname || "-"}</div>
                  <div className={`font-mono-tech text-sm ${s.clients > 0 ? "text-neon-green" : "text-muted-foreground/60"}`}>
                    {s.clients} / {s.sv_maxclients}
                  </div>
                  <div className="flex items-center">
                    {s.pswrd ? (
                      <Lock className="w-4 h-4 text-neon-red icon-glow" />
                    ) : (
                      <Unlock className="w-4 h-4 text-neon-green/80 icon-glow" />
                    )}
                  </div>
                </button>

                {expanded && <ServerDetail server={s} onCopy={() => copyConnect(s)} />}
              </div>
            );
          })}
        </div>
      </section>

      <footer className="text-center mt-8 mb-4 text-xs text-muted-foreground font-mono-tech">
        Data via <a className="text-cyan hover:underline" href="https://codservers.net" target="_blank" rel="noreferrer">codservers.net</a> · Live refresh every 2s
      </footer>
    </main>
  );
};

const StatCard = ({ icon, label, value, loading }: { icon: React.ReactNode; label: string; value: number; loading: boolean }) => (
  <div className="panel p-5 flex items-center gap-4 relative overflow-hidden">
    <div className="absolute inset-0 bg-gradient-to-br from-cyan/5 via-transparent to-transparent pointer-events-none" />
    <div className="relative w-12 h-12 rounded-lg border border-cyan/40 bg-cyan/5 flex items-center justify-center">
      {icon}
    </div>
    <div className="relative">
      <div className="label-chip">{label}</div>
      <div className="font-display text-3xl font-black mt-1 text-glow">
        {loading ? <span className="text-muted-foreground animate-pulse">--</span> : value.toLocaleString()}
      </div>
    </div>
  </div>
);

const CountryFlag = ({ iso, title }: { iso?: string; title?: string }) => {
  if (!iso) return <div className="w-7 h-5 rounded-sm bg-muted/40" />;
  const cp = iso.toUpperCase().split("").map((c) => 0x1f1e6 + c.charCodeAt(0) - 65);
  return (
    <span title={title} className="text-xl leading-none select-none">
      {String.fromCodePoint(...cp)}
    </span>
  );
};

const ServerDetail = ({ server, onCopy }: { server: CodServer; onCopy: () => void }) => {
  const sortedPlayers = [...(server.playerinfo || [])].sort(
    (a, b) => parseInt(b.score) - parseInt(a.score)
  );

  const mapImg = getMapImage(server.game, server.mapname);
  const links = detectLinks(
    server.sv_hostname,
    server.url,
    server.raw_info?._Website,
    server.raw_info?.sv_website,
    server.raw_info?._Discord,
    server.raw_info?.discord,
  );

  const locationFull = [server.city_name, server.country_name].filter(Boolean).join(", ") || "Unknown";
  const ownerName = server.owner || server.raw_info?.sv_owner || server.raw_info?._Admin || "";

  return (
    <div className="bg-panel-2/60 border-t border-border/40 px-4 md:px-6 py-6">
      <div className="grid lg:grid-cols-[300px_1fr] gap-6">
        <div className="space-y-4">
          <div className="aspect-[4/3] rounded-lg overflow-hidden border border-border/60 bg-panel-2 flex items-center justify-center relative">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan/10 via-transparent to-neon-purple/10 pointer-events-none" />
            {mapImg ? (
              <img
                src={mapImg}
                alt={server.mapname}
                loading="lazy"
                className="w-full h-full object-cover"
                onError={(e) => {
                  const el = e.currentTarget;
                  el.style.display = "none";
                  const sib = el.nextElementSibling as HTMLElement | null;
                  if (sib) sib.style.display = "flex";
                }}
              />
            ) : null}
            <div
              className="absolute inset-0 flex-col items-center justify-center text-center"
              style={{ display: mapImg ? "none" : "flex" }}
            >
              <div className="font-display text-2xl font-black text-neon-yellow text-glow">NO IMAGE</div>
              <div className="text-xs text-muted-foreground mt-1 font-mono-tech">{server.mapname}</div>
            </div>
          </div>

          <div className="space-y-2 text-sm">
            {ownerName && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <UserIcon className="w-4 h-4 text-neon-purple icon-glow" />
                <span className="text-foreground/90 truncate"><CodText text={ownerName} /></span>
              </div>
            )}
            <div className="flex items-center gap-2 text-muted-foreground">
              <MapPin className="w-4 h-4 text-cyan icon-glow" />
              <span>{locationFull}</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Network className="w-4 h-4 text-cyan icon-glow" />
              <span className="truncate">{server.network || "—"}</span>
            </div>
            {links.length === 0 ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <LinkIcon className="w-4 h-4 text-cyan icon-glow" />
                <span className="text-neon-blue/60">No website / discord</span>
              </div>
            ) : (
              links.map((l) => (
                <div key={l.href} className="flex items-center gap-2 text-muted-foreground">
                  {l.type === "discord" ? (
                    <MessageCircle className="w-4 h-4 text-neon-purple icon-glow" />
                  ) : (
                    <LinkIcon className="w-4 h-4 text-cyan icon-glow" />
                  )}
                  <a href={l.href} target="_blank" rel="noreferrer" className="text-neon-blue hover:underline truncate">
                    {l.label}
                  </a>
                </div>
              ))
            )}
          </div>

          <button
            onClick={onCopy}
            className="w-full flex items-center justify-between gap-3 bg-panel-2 border border-cyan/40 hover:border-cyan/80 rounded-lg px-3 py-2.5 transition group"
          >
            <span className="flex items-center gap-2 text-sm font-mono-tech text-cyan/90 truncate">
              <span className="text-cyan">›_</span>
              /connect {server.ip}:{server.port}
            </span>
            <Copy className="w-4 h-4 text-muted-foreground group-hover:text-cyan transition" />
          </button>
        </div>

        <div className="panel overflow-hidden">
          <div className="grid grid-cols-[1fr_100px] items-center px-4 py-3 bg-panel-2/80 border-b border-border/70 text-xs tracking-[0.2em] uppercase text-muted-foreground">
            <div className="flex items-center gap-2"><Users className="w-3.5 h-3.5 text-cyan icon-glow" /> Player</div>
            <div className="flex items-center justify-end gap-2"><Trophy className="w-3.5 h-3.5 text-neon-yellow icon-glow" /> Score <Signal className="w-3.5 h-3.5 text-neon-green icon-glow ml-1" /></div>
          </div>
          {sortedPlayers.length === 0 && (
            <div className="px-4 py-6 text-center text-muted-foreground font-mono-tech text-sm">// No players online</div>
          )}
          <div className="divide-y divide-border/30">
            {sortedPlayers.map((p, i) => (
              <div key={i} className="grid grid-cols-[1fr_100px] items-center px-4 py-2.5 row-hover">
                <div className="font-mono-tech text-sm truncate">
                  <CodText text={p.name} />
                </div>
                <div className="font-mono-tech text-sm text-right text-foreground/90">{p.score}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
